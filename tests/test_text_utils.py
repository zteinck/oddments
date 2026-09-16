from oddments import (
    add_border,
    wrap_docstring,
    )


def test_add_border(text, width):

    for align in ('left', 'right', 'center'):

        content = add_border(
            text=text,
            width=width,
            fixed_width=True,
            align=align,
            )

        print(f'\n{align.title()} Alignment:')
        print(content)


def test_wrap_docstring():
    raise NotImplementedError


if __name__ == '__main__':

    test_add_border(
        text='Testing Border',
        width=50,
        )