"""Tests for the user module"""


import hangups.user


USER_ID = hangups.user.UserID(1, 1)


def test_default_type_detection_empty_0():
    # missing names
    user = hangups.user.User(
        USER_ID,
        full_name='',
        first_name='',
        photo_url='',
        emails=[],
        is_self=False,
    )

    assert user.full_name == hangups.user.DEFAULT_NAME
    assert user.first_name == hangups.user.DEFAULT_NAME
    assert user.name_type == hangups.user.NameType.DEFAULT


def test_default_type_detection_empty_1():
    # missing names
    user = hangups.user.User(
        USER_ID,
        full_name=None,
        first_name=None,
        photo_url='',
        emails=[],
        is_self=False,
    )

    assert user.full_name == hangups.user.DEFAULT_NAME
    assert user.first_name == hangups.user.DEFAULT_NAME
    assert user.name_type == hangups.user.NameType.DEFAULT


def test_default_type_detection_201904():
    # default user in 201904
    user = hangups.user.User(
        USER_ID,
        full_name='unknown',
        first_name='unknown',
        photo_url='',
        emails=[],
        is_self=False,
    )

    assert user.full_name == hangups.user.DEFAULT_NAME
    assert user.first_name == hangups.user.DEFAULT_NAME
    assert user.name_type == hangups.user.NameType.DEFAULT


def test_real_type_0():
    # regular name
    user = hangups.user.User(
        USER_ID,
        full_name='Joe',
        first_name='Doe',
        photo_url='',
        emails=[],
        is_self=False,
    )

    assert user.full_name == 'Joe'
    assert user.first_name == 'Doe'
    assert user.name_type == hangups.user.NameType.REAL


def test_real_type_1():
    # both upper case
    user = hangups.user.User(
        USER_ID,
        full_name='Unknown',
        first_name='Unknown',
        photo_url='',
        emails=[],
        is_self=False,
    )

    assert user.full_name == 'Unknown'
    assert user.first_name == 'Unknown'
    assert user.name_type == hangups.user.NameType.REAL


def test_real_type_2():
    # display name lower case
    user = hangups.user.User(
        USER_ID,
        full_name='unknown',
        first_name='Unknown',
        photo_url='',
        emails=[],
        is_self=False,
    )

    assert user.full_name == 'unknown'
    assert user.first_name == 'Unknown'
    assert user.name_type == hangups.user.NameType.REAL


def test_real_type_3():
    # first name lower case
    user = hangups.user.User(
        USER_ID,
        full_name='Unknown',
        first_name='unknown',
        photo_url='',
        emails=[],
        is_self=False,
    )

    assert user.full_name == 'Unknown'
    assert user.first_name == 'unknown'
    assert user.name_type == hangups.user.NameType.REAL
