from lookout.core.analyzer import AnalyzerModel


class FunctionNameModel(AnalyzerModel):
    """
    Empty model.

    FunctionNameAnalyzer doesn't train on specific repositories.
    """
    NAME = "function-name"
    VENDOR = "source{d}"
