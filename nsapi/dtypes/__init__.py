import sys
import typing
import datetime
import logging

logger = logging.getLogger(__name__)

# class NSDataMeta(type):
#     def __call__(cls, data):
#         self = super().__call__(data)
#         for attr, typehint in typing.get_type_hints(cls).items():
#             if attr in data:
#                 setattr(self, attr, NSDataMeta.resolve_data_type(cls, typehint, data.pop(attr)))
#             else:
#                 setattr(self, attr, None)
#         if len(data) > 0:
#             print(f'{cls} received extra attributes: {data}')
#         return self
#
#     @classmethod
#     def resolve_data_type(mcs, cls, typehint, data):
#         origin = typing.get_origin(typehint)
#         if origin is not None and origin is typing.Union:
#             # Optional[...]
#             args = typing.get_args(typehint)
#             if len(args) == 2 and type(None) in args:
#                 typehint = args[0] if issubclass(args[1], type(None)) else args[1]
#                 return mcs.resolve_data_type(cls, typehint, data)
#             raise ValueError('Union[x, y] not supported')
#         if origin is not None and issubclass(origin, list):
#             # list[...]
#             typehint = typing.get_args(typehint)[0]
#             return [mcs.resolve_data_type(cls, typehint, item) for item in data]
#         if origin is not None and issubclass(origin, dict):
#             # dict[..., ...]
#             key_hint, value_hint = typing.get_args(typehint)
#             return {mcs.resolve_data_type(cls, key_hint, key): mcs.resolve_data_type(cls, value_hint, value) for key, value in data.items()}
#         if isinstance(typehint, str):
#             # "..."
#             dtype = getattr(sys.modules[cls.__module__], typehint)
#             return dtype(data)
#         if issubclass(typehint, datetime.datetime):
#             return datetime.datetime.strptime(data, "%Y-%m-%dT%H:%M:%S%z")
#         if issubclass(typehint, datetime.date):
#             return datetime.datetime.strptime(data, '%Y-%m-%d').date()
#         if typehint is not None and issubclass(typehint, NSData):
#             # NSData subclass
#             return typehint(data)
#         return data
#
#
# class NSData(metaclass=NSDataMeta):
#     def __init__(self, data):
#         ...

class NSData:
    def __init__(self, data=None, **kwargs):
        if data is None:
            data = kwargs
        cls = self.__class__
        data = {key.lower(): value for key,value in data.items()}
        for attr, typehint in typing.get_type_hints(cls).items():
            if attr.lower() in data:
                setattr(self, attr, cls._resolve_data_type(typehint, data.pop(attr.lower())))
            else:
                setattr(self, attr, None)
        if hasattr(self, '__post_init__'):
            self.__post_init__(data)
        if len(data) > 0:
            logger.warning(f'{cls} received extra attributes: {data}')

    @classmethod
    def _resolve_data_type(cls, typehint, data):
        origin = typing.get_origin(typehint)
        if origin is not None and origin is typing.Union:
            # Optional[...]
            args = typing.get_args(typehint)
            if len(args) == 2 and type(None) in args:
                typehint = args[0] if issubclass(args[1], type(None)) else args[1]
                return cls._resolve_data_type(typehint, data)
            raise ValueError('Union[x, y] not supported')
        if origin is not None and issubclass(origin, list):
            # list[...]
            typehint = typing.get_args(typehint)[0]
            return [cls._resolve_data_type(typehint, item) for item in data]
        if origin is not None and issubclass(origin, dict):
            # dict[..., ...]
            key_hint, value_hint = typing.get_args(typehint)
            return {cls._resolve_data_type(key_hint, key): cls._resolve_data_type(value_hint, value) for key, value in data.items()}
        if isinstance(typehint, str):
            # "..."
            dtype = getattr(sys.modules[cls.__module__], typehint)
            return dtype(data)
        if issubclass(typehint, datetime.datetime):
            return datetime.datetime.strptime(data, "%Y-%m-%dT%H:%M:%S%z")
        if issubclass(typehint, datetime.date):
            return datetime.datetime.strptime(data, '%Y-%m-%d').date()
        if typehint is not None and issubclass(typehint, NSData):
            # NSData subclass
            return typehint(data)
        return data
