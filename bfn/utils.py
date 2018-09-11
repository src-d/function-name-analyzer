import bz2
from collections import defaultdict
from difflib import SequenceMatcher
import importlib.util
from pathlib import Path
from typing import Dict, Iterable, List

from lookout.core.api.service_data_pb2 import File


def find_new_lines(before: File, after: File) -> List[int]:
    """
    Returns the new line numbers.

    :param before: the previous contents of the file.
    :param after: the new contents of the file.
    :return: list of line numbers new to `after`.
    """
    matcher = SequenceMatcher(a=before.content.decode("utf-8", "replace").splitlines(),
                              b=after.content.decode("utf-8", "replace").splitlines())
    result = []  # type: List[int]
    for action, _, _, j1, j2 in matcher.get_opcodes():
        if action in ("equal", "delete"):
            continue
        result.extend(range(j1 + 1, j2 + 1))
    return result


def files_by_language(files: Iterable[File]) -> Dict[str, Dict[str, File]]:
    """
    Sorts files by programming language and path.
    :param files: iterable of `File`-s.
    :return: dictionary with languages as keys and files mapped to paths as values.
    """
    result = defaultdict(dict)  # type: Dict[str, Dict[str, File]]
    for file in files:
        if not len(file.uast.children):
            continue
        result[file.language.lower()][file.path] = file
    return result


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract_bz2_if_not_exists(archive_path: Path) -> None:
    text_path = Path(archive_path.parent / archive_path.stem)
    with open(text_path, 'wb') as text, \
            bz2.BZ2File(archive_path, 'rb') as archive:
        for data in iter(lambda: archive.read(100 * 1024), b''):
            text.write(data)
