class DataProcessor(object):
    def __init__(self):
        self._loaded = False

    def load(self):
        raise NotImplementedError

    @property
    def is_loaded(self):
        return self._loaded
