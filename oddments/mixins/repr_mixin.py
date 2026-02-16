

class ReprMixin(object):

    #╭-------------------------------------------------------------------------╮
    #| Magic Methods                                                           |
    #╰-------------------------------------------------------------------------╯

    def __repr__(self):
        content = [f'{k}={v!r},' for k, v in self.__dict__.items()]
        content = '(' + ('\n' + ' ' * 4).join(['', *content, ')'])
        return self.__class__.__name__ + content