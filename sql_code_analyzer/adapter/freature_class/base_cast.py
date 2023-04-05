class BaseCast:
    @classmethod
    def cast(cls, object):
        """Cast an object from Class into a Class_."""
        object.__class__ = cls
        return object
