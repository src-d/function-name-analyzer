import argparse
import os
from pathlib import Path
import sys
from unittest.mock import patch

from utils import extract_bz2_if_not_exists, split_train_eval


def preprocess(args: argparse.Namespace) -> None:
    sys.path.append(str(Path(__file__).parent.parent / "OpenNMT-py"))
    import onmt.preprocess
    tokens_text_path = extract_bz2_if_not_exists(Path(args.tokens_archive))
    names_text_path = extract_bz2_if_not_exists(Path(args.names_archive))
    tokens_train, tokens_eval = split_train_eval(str(tokens_text_path))
    names_train, names_eval = split_train_eval(str(names_text_path))
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


def train(args: argparse.Namespace) -> None:
    sys.path.append(str(Path(__file__).parent.parent / "OpenNMT-py"))
    import onmt.train
    os.makedirs("models", exist_ok=True)
    command = ("train.py -data preprocessed/model -save_model models/model -gpuid 1 "
               "-valid_steps 10000 -save_checkpoint_steps 10000 -train_steps 1000000")
    if args.from_model:
        command += " -train_from %s" % args.from_model
    with patch("sys.argv", command.split(" ")):
        onmt.train.main()


def main() -> int:
    parser = argparse.ArgumentParser(description="Facilities to train OpenNMT model.")
    subparsers = parser.add_subparsers()
    parser_preprocess = subparsers.add_parser("preprocess",
                                              help="Preprocess the corpus with OpenNMT.")
    parser_preprocess.add_argument("tokens_archive", help="Path to the tokens train file.")
    parser_preprocess.add_argument("names_archive", help="Path to the names train file.")
    parser_preprocess.set_defaults(handler=preprocess)
    parser_train = subparsers.add_parser("train",
                                         help="Train on the preprocessed corpus.")
    parser_train.add_argument("--from-model", help="Checkpoint to start the training from.")
    parser_train.set_defaults(handler=train)
    args = parser.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
