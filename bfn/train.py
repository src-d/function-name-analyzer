import argparse
import os
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.append(str(Path(__file__).parent.parent / "OpenNMT-py"))
import onmt.train
import onmt.preprocess

from utils import extract_bz2_if_not_exists, split_train_eval


def main() -> int:
    parser = argparse.ArgumentParser(description="Facilities to train OpenNMT model.")
    parser.add_argument("tokens_archive", help="Path to the tokens train file.")
    parser.add_argument("names_archive", help="Path to the names train file.")
    args = parser.parse_args()
    tokens_text_path = extract_bz2_if_not_exists(Path(args.tokens_archive))
    names_text_path = extract_bz2_if_not_exists(Path(args.names_archive))
    tokens_train, tokens_eval = split_train_eval(str(tokens_text_path))
    names_train, names_eval = split_train_eval(str(names_text_path))
    if not (Path(__file__).parent.parent / "preprocessed" / "model.train.1.pt").exists():
        os.makedirs("preprocessed", exist_ok=True)
        command = ("preprocess.py -train_src %s -train_tgt %s -valid_src %s -valid_tgt %s "
                   "-save_data %s"
                   % (tokens_train,
                      names_train,
                      tokens_eval,
                      names_eval,
                      "preprocessed/model"))
        with patch("sys.argv", command.split(" ")):
            onmt.preprocess.main()
    os.makedirs("models", exist_ok=True)
    command = ("train.py -data preprocessed/model -save_model models/model -gpuid 1 "
               "-valid_steps 10000 -save_checkpoint_steps 10000")
    with patch("sys.argv", command.split(" ")):
        onmt.train.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
