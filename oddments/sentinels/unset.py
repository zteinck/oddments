

class Unset:
    '''
    Description
    --------------------
    Sentinel class representing an explicitly unset parameter.

    Class Attributes
    --------------------
    _instance : Unset
        Cached singleton instance.

    Instance Attributes
    --------------------
    None
    '''

    #╭-------------------------------------------------------------------------╮
    #| Class Attributes                                                        |
    #╰-------------------------------------------------------------------------╯

    __slots__ = ()
    _instance = None


    #╭-------------------------------------------------------------------------╮
    #| Magic Methods                                                           |
    #╰-------------------------------------------------------------------------╯

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


    def __bool__(self):
        raise TypeError(
            "UNSET sentinel has no truth value. Use 'is UNSET' instead."
            )


    def __copy__(self):
        return self


    def __deepcopy__(self, memo):
        return self


    def __reduce__(self):
        # Ensures unpickling reconstructs via __new__
        return (self.__class__, ())


    def __repr__(self):
        return self.__class__.__name__.upper()


# Sentinel representing an explicitly unset parameter.
UNSET = Unset()