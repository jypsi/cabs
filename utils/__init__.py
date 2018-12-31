import importlib
import re


def import_path(path):
    """Import from dotted path"""
    module_path, obj = re.split('\.(?=[\w_\-\d]+$)', path)
    module = importlib.import_module(module_path)
    return getattr(module, obj)
