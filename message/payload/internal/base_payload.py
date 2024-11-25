from .exceptions import InvalidFieldException, MissingFieldException
from .parsable_payload import ParsablePayload
from typing import Generic


class Payload():
    @classmethod
    def _from_dict(cls, dict: dict):
        kwargs = {}

        missing = set(cls.__annotations__.keys()) - set(dict.keys())
        if len(missing) > 0:
            # 필요한 key가 없음
            raise MissingFieldException(missing)

        for key in dict:
            if not key in cls.__annotations__:
                # event의 없는 key
                raise InvalidFieldException(key, dict[key])

            t = cls.__annotations__[key]
            if hasattr(t, "__origin__") and t.__origin__ == ParsablePayload:
                if len(t.__args__) != 1:
                    raise
                try:
                    kwargs[key] = t.__args__[0](**dict[key])
                except:
                    raise
                continue

            if issubclass(t, Payload):
                try:
                    kwargs[key] = t._from_dict(dict[key])
                except InvalidFieldException as e:
                    raise InvalidFieldException(key, e)
                except MissingFieldException as e:
                    raise MissingFieldException(key, e)
                continue

            if not type(dict[key]) == t:
                # 잘못된 형식의 data
                raise InvalidFieldException(key, dict[key])

            kwargs[key] = t(dict[key])

        return cls(**kwargs)


if __name__ == "__main__":
    pass
