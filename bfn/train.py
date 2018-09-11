import argparse
from pathlib import Path
import sys

sys.path.append(str(Path(__file__) / "OpenNMT-py"))
import train
import preprocess


from utils import extract_bz2_if_not_exists, load_module


def main() -> int:
    parser = argparse.ArgumentParser(description="Facilities to train OpenNMT model.")
    parser.add_argument("train_tokens_archive", help="Path to the tokens train file.")
    parser.add_argument("train_names_archive", help="Path to the names train file.")
    args = parser.parse_args()
    train_tokens_archive_path = Path(args.train_tokens_archive)
    train_names_archive_path = Path(args.train_names_archive)
    extract_bz2_if_not_exists(train_tokens_archive_path)
    extract_bz2_if_not_exists(train_names_archive_path)
    print(preprocess)
    return 0


if __name__ == "__main__":
    sys.exit(main())
