class BaseCast:
    @classmethod
    def cast(cls, instance):
        """Cast an object from Class into a Class_."""
        instance.__class__ = cls
        return instance
