from textwrap import wrap as wrap_text

from ..validation import Validator

_SPACE_CHAR = ' '
_NEW_LINE_CHAR = '\n'


def add_border(text, width=100, fixed_width=False, align='left'):
    '''
    Description
    ------------
    Adds a border around text.

    Parameters
    ------------
    text : str
        Text to enclose in a border.
    width : int
        'textwrap.wrap' width argument. If width=1, the text is printed
        vertically.
    fixed_width : bool
        • True → the width of the border will equal the 'width' argument
            value.
        • False → the width of the border is capped at the length of the
            longest line in the text.
    align : str
        • 'left' → aligns text along the left margin
        • 'center' → aligns text in the center between the left and right
            margins
        • 'right' → aligns text along the right margin

    Returns
    ------------
    result : str
        Text enclosed in a border.
    '''
    (
    Validator(
        types=bool
        )
    .validate(
        fixed_width=fixed_width
        )
    )

    (
    Validator(
        types=str,
        whitelist=['left','right','center'],
        )
    .validate(
        align=align
        )
    )

    lines = wrap_text(
        text=_SPACE_CHAR.join(text.split()),
        width=width,
        )

    max_width = (
        width
        if fixed_width
        else len(max(lines, key=len))
        )

    border_edge = '-' * (max_width + 2)
    top_border = '╭' + border_edge + '╮'
    bottom_border = '╰' + border_edge + '╯'
    side_border = '|'

    rows = []

    for line in lines:
        total_pad = max_width - len(line)

        if align == 'left':
            left_pad, right_pad = 0, total_pad
        elif align == 'right':
            left_pad, right_pad = total_pad, 0
        else:
            left_pad, right_pad = (
                ((total_pad + x) // 2)
                for x in (0, 1)
                )

        left_pad, right_pad = (
            ''.join([_SPACE_CHAR] * x)
            for x in (left_pad, right_pad)
            )

        row = _SPACE_CHAR.join((
            side_border,
            ''.join((left_pad, line, right_pad)),
            side_border,
            ))

        rows.append(row)

    result = _NEW_LINE_CHAR.join((
        top_border,
        _NEW_LINE_CHAR.join(rows),
        bottom_border,
        ))

    return result


def wrap_docstring(text, indents=0, indent_width=4, line_width=79):
    '''
    Description
    ------------
    Wrap docstring text so that it adheres to the PEP 8 maximum line length.

    Parameters
    ------------
    text : str
        Text to wrap.
    indents : int
        Number of indentations.
    indent_width : int
        Number of spaces per indentation.
    line_width : int
        Maximum allowed line length, including indentation.

    Returns
    ------------
    result : str
        Wrapped docstring text.
    '''
    indent_limit = line_width // indent_width

    if indents > indent_limit:
        raise ValueError(
            f'Number of indents ({indents}) exceeds the limit '
            f'({indent_limit}).'
            )

    text = _SPACE_CHAR.join(text.split())
    width = line_width - indents * indent_width
    lines = wrap_text(text=text, width=width)
    result = _NEW_LINE_CHAR.join(lines)
    return result