import os
import joblib

class MLModelRegistry:
    """Registry and loader for pre-trained or cached machine learning models."""
    _models = {}

    @classmethod
    def get_model(cls, model_name):
        return cls._models.get(model_name)

    @classmethod
    def register_model(cls, model_name, model_obj):
        cls._models[model_name] = model_obj

    @classmethod
    def save_model(cls, model_name, model_obj, directory=None):
        if directory is None:
            directory = os.path.dirname(__file__)
        path = os.path.join(directory, f"{model_name}.pkl")
        joblib.dump(model_obj, path)
        cls._models[model_name] = model_obj
        return path

    @classmethod
    def load_model(cls, model_name, directory=None):
        if directory is None:
            directory = os.path.dirname(__file__)
        path = os.path.join(directory, f"{model_name}.pkl")
        if os.path.exists(path):
            cls._models[model_name] = joblib.load(path)
            return cls._models[model_name]
        return None

