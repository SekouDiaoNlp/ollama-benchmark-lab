class RunRegistry:
    """
    Stores full historical execution metadata.
    """

    def __init__(self):
        self.registry = []

    def add(self, run: dict):
        self.registry.append(run)

    def query_by_model(self, model_name: str):
        return [
            r for r in self.registry
            if r.get("config", {}).get("model") == model_name
        ]