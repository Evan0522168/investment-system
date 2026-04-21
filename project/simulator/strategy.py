class Strategy:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description

    def signal(self, df):
        raise NotImplementedError

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__
        }
