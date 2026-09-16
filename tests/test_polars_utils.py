import oddments as odd
import polars as pl


def test_assert_no_nulls():

    df = pl.DataFrame({
        'a': [None, 1, 2],
        'b': ['dog', 'cat', None],
        'c': [1.0, 2.0, 3.0],
        'd': ['red', 'blue', 'green'],
        'e': [None, None, False],
        'f': [False, None, True],
        })

    odd.assert_no_nulls(df)


def test_assert_unique():

    df = pl.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'pet': ['dog', 'cat', 'cat', 'fish', 'cat'],
        'color': ['red', 'blue', 'pink', 'grey', 'blue'],
        'is_mammal': [True, None, False, False, True],
        })

    # no error, all unique
    odd.assert_unique(df, subset=['id', 'pet'])

    # error on duplicate
    odd.assert_unique(df, subset=['pet','color'])

    # error on null
    odd.assert_unique(df, subset=['pet','is_mammal'])


def test_trim_nulls():

    df = pl.DataFrame({
        'id': [1, 2, 3, 4, None],
        'pet': [None, None, 'cat', 'fish', 'cat'],
        'color': ['red', 'blue', None, 'grey', 'blue'],
        })

    a = odd.trim_nulls(df)

    b = odd.trim_nulls(
        df,
        subset=['pet', 'color'],
        which='leading',
        how='any',
        )

    c = odd.trim_nulls(
        df,
        which='trailing',
        how='any',
        allow_nulls=True,
        )


def test_purge_whitespace():

    df = pl.DataFrame({
        ' id ': [1, 2, 3, 4, None],
        ' pet': [None, None, ' cat ', ' ', '\n\n bird'],
        'color ': ['', 'blue', None, '  grey', 'blue '],
        })

    result = odd.purge_whitespace(df)

    print(result.columns)
    print(result.rows())



if __name__ == '__main__':

    test_assert_no_nulls()
    test_assert_unique()
    test_trim_nulls()
    test_purge_whitespace()