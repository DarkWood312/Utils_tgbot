from dataclasses import dataclass, fields


def fill_in_dataclass(fill: dict, dataclass_: dataclass, **additional_fields):
    valid_fields = [field.name for field in fields(dataclass_)]
    filtered = {k: v for k, v in fill.items() if k in valid_fields} | additional_fields
    return dataclass_(**filtered)


def post_init_wrapper(cls):
    original_post = getattr(cls, "__post_init__", None)

    def __post_init__(self, *args, **kwargs):
        if original_post:
            original_post(self, *args, **kwargs)

        url = getattr(self, "faceit_url", None)
        if url is not None:
            object.__setattr__(self, "faceit_url", url.replace("{lang}", "ru"))

    cls.__post_init__ = __post_init__
    return cls