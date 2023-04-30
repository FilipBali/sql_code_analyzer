class BaseCast:
    @classmethod
    def cast(cls, instance):
        """Cast an object from library class into a adapter class."""
        instance.__class__ = cls
        return instance
