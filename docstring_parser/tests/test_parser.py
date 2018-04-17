import typing as T

import pytest

from docstring_parser import parse


@pytest.mark.parametrize('source, expected', [
    ('', None),
    ('\n', None),
    ('Short description', 'Short description'),
    ('\nShort description\n', 'Short description'),
    ('\n   Short description\n', 'Short description'),
])
def test_short_description(source: str, expected: str) -> None:
    docstring = parse(source)
    assert docstring.short_description == expected
    assert docstring.long_description is None
    assert docstring.meta == []


@pytest.mark.parametrize(
    'source, expected_short_desc, expected_long_desc, expected_blank',
    [
        (
            'Short description\n\nLong description',
            'Short description',
            'Long description',
            True
        ),

        (
            '''
            Short description

            Long description
            ''',
            'Short description',
            'Long description',
            True
        ),

        (
            '''
            Short description

            Long description
            Second line
            ''',
            'Short description',
            'Long description\nSecond line',
            True
        ),

        (
            'Short description\nLong description',
            'Short description',
            'Long description',
            False
        ),

        (
            '''
            Short description
            Long description
            ''',
            'Short description',
            'Long description',
            False
        ),

        (
            '\nShort description\nLong description\n',
            'Short description',
            'Long description',
            False
        ),

        (
            '''
            Short description
            Long description
            Second line
            ''',
            'Short description',
            'Long description\nSecond line',
            False
        ),
    ]
)
def test_long_description(
        source: str,
        expected_short_desc: str,
        expected_long_desc: str,
        expected_blank: bool
) -> None:
    docstring = parse(source)
    assert docstring.short_description == expected_short_desc
    assert docstring.long_description == expected_long_desc
    assert docstring.blank_after_short_description == expected_blank
    assert docstring.meta == []


@pytest.mark.parametrize(
    'source, expected_short_desc, expected_long_desc, '
    'expected_blank_short_desc, expected_blank_long_desc',
    [
        (
            '''
            Short description
            :param: asd
            ''',
            'Short description', None, False, False
        ),

        (
            '''
            Short description
            Long description
            :param: asd
            ''',
            'Short description', 'Long description', False, False
        ),

        (
            '''
            Short description
            First line
                Second line
            :param: asd
            ''',
            'Short description', 'First line\n    Second line', False, False
        ),

        (
            '''
            Short description

            First line
                Second line
            :param: asd
            ''',
            'Short description', 'First line\n    Second line', True, False
        ),

        (
            '''
            Short description

            First line
                Second line

            :param: asd
            ''',
            'Short description', 'First line\n    Second line', True, True
        ),

        (
            '''
            :param: asd
            ''',
            None, None, False, False
        )
    ]
)
def test_meta_newlines(
        source: str,
        expected_short_desc: T.Optional[str],
        expected_long_desc: T.Optional[str],
        expected_blank_short_desc: bool,
        expected_blank_long_desc: bool
) -> None:
    docstring = parse(source)
    assert docstring.short_description == expected_short_desc
    assert docstring.long_description == expected_long_desc
    assert docstring.blank_after_short_description == expected_blank_short_desc
    assert docstring.blank_after_long_description == expected_blank_long_desc
    assert len(docstring.meta) == 1


def test_meta_with_multiline_description() -> None:
    docstring = parse(
        '''
        Short description

        :param: asd
            1
                2
            3
        ''')
    assert docstring.short_description == 'Short description'
    assert len(docstring.meta) == 1
    assert docstring.meta[0].args == ['param']
    assert docstring.meta[0].description == 'asd\n1\n    2\n3'


def test_multiple_meta() -> None:
    docstring = parse(
        '''
        Short description

        :param: asd
            1
                2
            3
        :param2: herp
        :param3: derp
        ''')
    assert docstring.short_description == 'Short description'
    assert len(docstring.meta) == 3
    assert docstring.meta[0].args == ['param']
    assert docstring.meta[0].description == 'asd\n1\n    2\n3'
    assert docstring.meta[1].args == ['param2']
    assert docstring.meta[1].description == 'herp'
    assert docstring.meta[2].args == ['param3']
    assert docstring.meta[2].description == 'derp'


def test_params() -> None:
    docstring = parse('Short description')
    assert len(docstring.params) == 0

    docstring = parse(
        '''
        Short description

        :param name: description 1
        :param int priority: description 2
        :param str sender: description 3
        :param: invalid
        ''')
    assert len(docstring.params) == 4
    assert docstring.params[0].arg_name == 'name'
    assert docstring.params[0].type_name is None
    assert docstring.params[0].description == 'description 1'
    assert docstring.params[1].arg_name == 'priority'
    assert docstring.params[1].type_name == 'int'
    assert docstring.params[1].description == 'description 2'
    assert docstring.params[2].arg_name == 'sender'
    assert docstring.params[2].type_name == 'str'
    assert docstring.params[2].description == 'description 3'
    assert docstring.params[3].arg_name is None
    assert docstring.params[3].type_name is None
    assert docstring.params[3].description == 'invalid'


def test_returns() -> None:
    docstring = parse(
        '''
        Short description
        ''')
    assert docstring.returns is None

    docstring = parse(
        '''
        Short description
        :returns: description
        ''')
    assert docstring.returns is not None
    assert docstring.returns.type_name is None
    assert docstring.returns.description == 'description'

    docstring = parse(
        '''
        Short description
        :returns int: description
        ''')
    assert docstring.returns is not None
    assert docstring.returns.type_name == 'int'
    assert docstring.returns.description == 'description'


def test_raises() -> None:
    docstring = parse(
        '''
        Short description
        ''')
    assert len(docstring.raises) == 0

    docstring = parse(
        '''
        Short description
        :raises: description
        ''')
    assert len(docstring.raises) == 1
    assert docstring.raises[0].type_name is None
    assert docstring.raises[0].description == 'description'

    docstring = parse(
        '''
        Short description
        :raises ValueError: description
        ''')
    assert len(docstring.raises) == 1
    assert docstring.raises[0].type_name == 'ValueError'
    assert docstring.raises[0].description == 'description'
