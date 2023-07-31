class SingletonMeta(type):
    _instances = dict()
    def __call__(cls):
        if cls not in SingletonMeta._instances:
            cls._instances[cls] = super().__call__()
        return cls._instances[cls]