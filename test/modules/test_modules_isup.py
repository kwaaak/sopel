# coding=utf-8
"""Tests for Sopel's ``remind`` plugin"""
from __future__ import unicode_literals, absolute_import, print_function, division

import pytest

from sopel.modules import isup


VALID_SITE_URLS = (
    # no TLD, no scheme
    ('example', 'http://example.com'),
    # no scheme
    ('www.example.com', 'http://www.example.com'),
    # with scheme
    ('http://example.com', 'http://example.com'),
    ('https://example.com', 'https://example.com'),
    # with scheme and URL path
    ('http://example.com/path', 'http://example.com/path'),
    ('https://example.com/path', 'https://example.com/path'),
    # with scheme, URL path, and query string
    ('http://example.com/path?p=val', 'http://example.com/path?p=val'),
    ('https://example.com/path?p=val', 'https://example.com/path?p=val'),
    # not .com TLD
    ('example.io', 'http://example.io'),
    ('www.example.io', 'http://www.example.io'),
)


@pytest.mark.parametrize('site, expected', VALID_SITE_URLS)
def test_get_site_url(site, expected):
    assert isup.get_site_url(site) == expected


INVALID_SITE_URLS = (
    '',  # empty
    '      ',  # empty once stripped
    'steam://browsemedia',  # invalid protocol
    '://',  # invalid protocol (that's a weird one)
)


@pytest.mark.parametrize('site', INVALID_SITE_URLS)
def test_get_site_url_invalid(site):
    with pytest.raises(ValueError):
        isup.get_site_url(site)
