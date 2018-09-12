import bz2
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

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


def extract_bz2_if_not_exists(archive_path: Path) -> Path:
    text_path = Path(archive_path.parent / archive_path.stem)
    if not text_path.exists():
        with open(text_path, 'wb') as text, \
                bz2.BZ2File(archive_path, 'rb') as archive:
            for data in iter(lambda: archive.read(100 * 1024), b''):
                text.write(data)
    return text_path


def split_train_eval(filepath: str) -> Tuple[str, str]:
    train_path = filepath + ".train"
    eval_path = filepath + ".eval"
    with open(filepath, 'r') as fh, \
            open(train_path, "w") as fh_train, \
            open(eval_path, "w") as fh_eval:
        lines = fh.readlines()
        fh_train.writelines(lines[:-10000])
        fh_eval.writelines(lines[-10000:])
    return train_path, eval_path
