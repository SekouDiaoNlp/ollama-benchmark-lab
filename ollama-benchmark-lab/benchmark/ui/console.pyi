class Console:
    GREEN: str
    ORANGE: str
    RED: str
    WHITE: str
    RESET: str
    @staticmethod
    def ok(msg: str): ...
    @staticmethod
    def warn(msg: str): ...
    @staticmethod
    def error(msg: str): ...
    @staticmethod
    def info(msg: str): ...
