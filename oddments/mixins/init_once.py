

class InitOnceMixin:

    def _init_internal_attr(self, name, value):
        if not isinstance(name, str):
            raise TypeError(
                f"'name' must be a string, got: {type(name).__name__}"
                )

        if name.startswith('_'):
            raise ValueError(
                "'name' argument must not begin with an underscore, got: "
                f"{name!r}"
                )

        attr = f'_{name}'

        if hasattr(self, attr):
            raise RuntimeError(
                f'Attribute {attr!r} already exists.'
                )

        setattr(self, attr, value)