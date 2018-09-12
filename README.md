# Function Name Analyzer

This analyzer applies a translation model from function identifiers to function names.

## Installation

1. Install [PyTorch](https://pytorch.org/) 0.4
2. Install the dependencies

        pip install -r requirements.txt
3. Install the package

        pip install -e .

## Usage

1. Start the lookout python server

        analyzer run fna --server 0.0.0.0:2000 --db sqlite:////tmp/lookout.sqlite --fs /tmp --log-level DEBUG
2. Simulate a pull request with the [`lookout`](https://github.com/src-d/lookout) binary

        lookout review -v ipv4://localhost:2000 --to ... --from ...

You should take care to have java files that changed inbetween the `to` and `from` revision or the
analyzer won't find any function name to run on.
