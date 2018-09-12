from lookout.core.analyzer import AnalyzerModel


class FunctionNameModel(AnalyzerModel):
    """
    Empty model.

    FunctionNameAnalyzer doesn't train on specific repositories.
    """
    NAME = "function-name"
    VENDOR = "source{d}"

    def _generate_tree(self):
        return {}

    def _load_tree(self, tree):
        pass