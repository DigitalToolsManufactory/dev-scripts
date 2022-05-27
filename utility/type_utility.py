from typing import Any, Optional, Union, Callable


def get_or_else(maybe_value: Optional[Any], fallback: Union[Any, Callable[[], Any]]) -> Any:
    if maybe_value is not None:
        return maybe_value

    if isinstance(fallback, Callable):
        return fallback()

    return fallback


def get_or_raise(maybe_value: Optional[Any], error: Optional[Union[Exception, Callable[[], Exception]]] = None) -> Any:
    if maybe_value is not None:
        return maybe_value

    if error is None:
        raise AssertionError("Value must not be None")

    if isinstance(error, Exception):
        raise error

    raise error()
