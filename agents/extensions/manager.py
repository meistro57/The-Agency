import importlib.util
import logging
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ExtensionManager:
    """Simple plugin loader for agent extensions."""

    REGISTRY = {}

    @classmethod
    def load_extensions(cls, directory: str) -> None:
        for fname in os.listdir(directory):
            if fname.endswith('.py') and fname != '__init__.py':
                path = os.path.join(directory, fname)
                mod_name = os.path.splitext(fname)[0]
                try:
                    spec = importlib.util.spec_from_file_location(mod_name, path)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)  # type: ignore
                    if hasattr(mod, 'register'):
                        mod.register(cls)
                        logger.info(f"Loaded extension {fname}")
                except Exception as e:
                    logger.error(f"Failed to load {fname}: {e}")

    @classmethod
    def register(cls, name: str, obj) -> None:
        cls.REGISTRY[name] = obj

    @classmethod
    def get(cls, name: str):
        return cls.REGISTRY.get(name)

    @classmethod
    def list_extensions(cls):
        return list(cls.REGISTRY.keys())
