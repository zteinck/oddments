from oddments import ReprMixin


class Dog(ReprMixin):

    species = 'Canis familiaris'

    def __init__(self, name, breed):
        self.name = name
        self.breed = breed


class Cat(ReprMixin):

    species = 'Felis catus'
    _repr_attrs = ['species', 'mischievous']

    def __init__(self, name, mischievous=True):
        self.name = name
        self.mischievous = mischievous


if __name__ == '__main__':

    dog = Dog(name='Fido', breed='Maltese')
    print(dog)

    cat = Cat('Whiskers')
    print(cat)