from typing import Type, cast

from sql_code_analyzer.adapter.base_class import BaseClass
from sql_code_analyzer.adapter.freature_class.accept_visitor import AcceptVisitor
from sql_code_analyzer.adapter.freature_class.base_cast import BaseCast


def class_factory(name, library_class, args_names=None):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key not in args_names:
                raise TypeError("Argument %s not valid for %s"
                    % (key, self.__class__.__name__))
            setattr(self, key, value)
        BaseClass.__init__(self, name[:-len("Class")])

    inherit_classes = (library_class, BaseCast, AcceptVisitor)
    return cast(Type[BaseCast], type(name, inherit_classes, {"__init__": __init__}))
