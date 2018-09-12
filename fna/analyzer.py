import logging
import tempfile
from typing import Any, Dict, Optional, Sequence

from lookout.core.analyzer import Analyzer, ReferencePointer
from lookout.core.api.service_analyzer_pb2 import Comment
from lookout.core.api.service_data_pb2_grpc import DataStub
from lookout.core.data_requests import with_changed_uasts_and_contents, with_uasts_and_contents
from sourced.ml.algorithms import uast2sequence, TokenParser
from sourced.ml.utils import IDENTIFIER, FUNCTION, NAME

from fna.model import FunctionNameModel
from fna.utils import find_new_lines, files_by_language


class FunctionNameAnalyzer(Analyzer):
    log = logging.getLogger("FunctionNameAnalyzer")
    model_type = FunctionNameModel
    version = "1"
    description = "Analyzer that suggests function names."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token_parser = TokenParser(min_split_length=1, single_shot=True)

    @with_changed_uasts_and_contents
    def analyze(self, ptr_from: ReferencePointer, ptr_to: ReferencePointer,
                data_request_stub: DataStub, **data) -> [Comment]:
        comments = []
        changes = list(data["changes"])
        base_files = files_by_language(c.base for c in changes)
        head_files = files_by_language(c.head for c in changes)
        for lang, lang_head_files in head_files.items():
            for path, file in lang_head_files.items():
                try:
                    prev_file = base_files[lang][path]
                except KeyError:
                    lines = None
                else:
                    lines = [find_new_lines(prev_file, file)]
                X = self._extract_features(file, lines)
                self.log.debug("predicting values for %d samples", len(X))
        return comments

    @classmethod
    @with_uasts_and_contents
    def train(cls, ptr: ReferencePointer, config: Dict[str, Any], data_request_stub: DataStub,
              **data) -> FunctionNameModel:
        """
        Dummy train.

        :param ptr: Git repository state pointer.
        :param config: configuration dict.
        :param data: contains "files" - the list of files in the pointed state.
        :param data_request_stub: connection to the Lookout data retrieval service, not used.
        :return: FunctionNameModel dummy model.
        """
        return FunctionNameModel().construct(cls, ptr)

    def process_node(self, node, last_position):
        if IDENTIFIER in node.roles and node.token and FUNCTION not in node.roles:
            for x in self.token_parser(node.token):
                yield x, last_position

    def process_uast(self, uast):
        stack = [(uast, [0, 0])]
        while stack:
            node, last_position = stack.pop()
            if node.start_position.line != 0:
                # A lot of Nodes do not have position
                # It is good heuristic to take the last Node in tree with a position.
                last_position[0] = node.start_position.line
                last_position[1] = 0
            if node.start_position.col != 0:
                last_position[1] = node.start_position.col
            yield from self.process_node(node, last_position)
            stack.extend([(child, list(last_position)) for child in node.children])

    def extract_functions_from_uast(self, uast: "bblfsh.Node"):
        for node in uast2sequence(uast):
            if node.internal_type != "MethodDeclaration":
                continue
            for subnode in node.children:
                if FUNCTION not in subnode.roles and NAME not in subnode.roles:
                    continue
                name = subnode.token
                break
            yield (name, node.start_position.line, node.end_position.line,
                   [token for token, pos in
                    sorted(self.process_uast(node), key=lambda x: x[1])
                    if len(token) >= 5])

    def get_affected_functions(self, uast, lines: Optional[Sequence[int]]):
        functions_info = list(self.extract_functions_from_uast(uast))
        i = 0
        res = []
        for line in sorted(lines):
            while i < len(functions_info):
                if functions_info[i][1] <= line <= functions_info[i][2]:
                    res.append(functions_info[i])
                    i += 1
                    break
                elif line < functions_info[i][1]:
                    break
                elif line > functions_info[i][2]:
                    i += 1

        return res

    @staticmethod
    def to_nmt_files(functions_info):
        func_start = []
        with tempfile.NamedTemporaryFile(delete=False, mode="w") as func_names:
            with tempfile.NamedTemporaryFile(delete=False, mode="w") as func_tokens:
                for name, start_line, end_line, tokens in functions_info:
                    func_names.write(" ".join(list(name)) + "\n")
                    func_tokens.write(" ".join(tokens) + "\n")
                    func_start.append(start_line)
        return func_names.name, func_tokens.name, func_start

    def _extract_features(self, file, lines: Optional[Sequence[int]]):
        if file.language != "java":
            raise ValueError("Only java language is supported now")
        if lines:
            affected_functions = self.get_affected_functions(file.uast, lines)
        else:
            # all function are affected because the file is new
            affected_functions = self.extract_functions_from_uast(file.uast)

        return self.to_nmt_files(affected_functions)
