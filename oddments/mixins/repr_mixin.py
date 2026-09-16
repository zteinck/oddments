

class ReprMixin:

    #╭-------------------------------------------------------------------------╮
    #| Magic Methods                                                           |
    #╰-------------------------------------------------------------------------╯

    def __repr__(self):
        repr_attrs = getattr(self, '_repr_attrs', None)

        if repr_attrs is None:
            data = {
                k: v for k, v in
                self.__dict__.items()
                }
        else:
            data = {
                k: getattr(self, k)
                for k in repr_attrs
                }

        content = ', '.join(
            f'{k}={v!r}'
            for k, v in data.items()
            )

        text = f'{self.__class__.__name__}({content})'
        return text