import logging
from typing import Any, Dict

from lookout.core.analyzer import Analyzer, ReferencePointer
from lookout.core.api.service_analyzer_pb2 import Comment
from lookout.core.api.service_data_pb2_grpc import DataStub
from lookout.core.data_requests import with_changed_uasts_and_contents, with_uasts_and_contents
from lookout.style.format.model import FormatModel

from .model import FunctionNameModel
from .utils import find_new_lines, files_by_language


class FunctionNameAnalyzer(Analyzer):
    log = logging.getLogger("FunctionNameAnalyzer")
    model_type = FunctionNameModel
    version = "1"
    description = "Analyzer that suggests function names."

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
        return FormatModel().construct(cls, ptr)

    def _extract_features(self, file, lines):
        raise NotImplemented()
