

from typing import List
from imbox.parser import *
import pytest


def test_decode_mail_header():
    valid_utf8_header = "=?utf-8?b?VGVzdCBFbWFpbCBIZWFkZXI=?="

    lv = decode_mail_header(valid_utf8_header)
    assert lv == "Test Email Header"

    # Testing header with non-UTF8 encoding
    valid_iso8859_header = "=?iso-8859-1?b?VGVzdCBFbWFpbCBIZWFkZXI=?="
    lj = decode_mail_header(valid_iso8859_header)
    assert lj == "Test Email Header"

    # Test invalid header
    invalid_header = "=?utf-8?b?SGVsbG8gd29ybGQh======?="  # 'Hello world!' encoded in Base64 with invalid padding
    li = decode_mail_header(invalid_header)
    assert li == "Hello world!"

    # Test header with unknown charset should default to 'us-ascii'
    unknown_charset_header = "=?x-unknown?b?SGVsbG8gd29ybGQh?="
    lu = decode_mail_header(unknown_charset_header)
    assert lu == "Hello world!"
