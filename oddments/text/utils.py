from textwrap import wrap as wrap_text

from ..validation import validate_value


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
        'textwrap.wrap' width argument. If width=1, the text is printed vertically.
    fixed_width : bool
        • True ➜ the width of the border will equal the 'width' argument value.
        • False ➜ the width of the border is capped at the length of the longest
                   line in the text.
    align : str
        • 'left' ➜ aligns text along the left margin
        • 'center' ➜ aligns text in the center between the left and right margins
        • 'right' ➜ aligns text along the right margin

    Returns
    ------------
    out : str
        Text enclosed in a border.
    '''
    lines = wrap_text(' '.join(text.split()), width)
    max_width = width if fixed_width else len(max(lines, key=len))

    validate_value(
        value=align,
        attr='align',
        types=str,
        whitelist=['left','right','center'],
        )

    border_edge = '-' * (max_width + 2)
    top_border = '╭' + border_edge + '╮'
    bottom_border = '╰' + border_edge + '╯'

    if align in 'left':
        content = [
            ('| ' + line + ''.join([' '] * (max_width - len(line))) + ' |')
            for line in lines
            ]

    elif align == 'right':
        content = [
            ('| ' + ''.join([' '] * (max_width - len(line))) + line + ' |')
            for line in lines
            ]

    elif align == 'center':
        content = [
            ('| ' + ''.join([' '] * ((max_width - len(line)) // 2)) + line +
            ''.join([' '] * ((max_width - len(line) + 1) // 2)) + ' |')
            for line in lines
            ]

    out = '\n'.join([top_border, '\n'.join(content), bottom_border])

    return out