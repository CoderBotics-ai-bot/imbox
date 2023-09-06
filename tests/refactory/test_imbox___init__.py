from imbox.imap import ImapTransport
import imaplib
from imbox.imbox import *

from imbox import Imbox
from ssl import SSLContext

import pytest


from email.policy import Policy
from unittest.mock import MagicMock, patch
from typing import Optional


class TestImboxInit:
    @pytest.fixture
    def mock_imap_interface(self, monkeypatch):
        mock_imap = MagicMock(spec=ImapTransport)
        monkeypatch.setattr("imbox.imap.ImapTransport", mock_imap)
        return mock_imap

    def test_init_without_vendor(self, mock_imap_interface):
        imbox_instance = Imbox(hostname="hostname", username="user", password="pass")
        assert imbox_instance.hostname == "hostname"
        assert imbox_instance.username == "user"
        assert imbox_instance.password == "pass"
        assert imbox_instance.vendor is None
        mock_imap_interface.assert_called_once_with(
            "hostname", ssl=True, port=None, ssl_context=None, starttls=False
        )

    def test_init_with_vendor(self, mock_imap_interface):
        imbox_instance = Imbox(
            hostname="hostname", username="user", password="pass", vendor="gmail"
        )

        assert imbox_instance.vendor == "gmail"
        assert imbox_instance.authentication_error_message is not None

    @patch("logging.getLogger")
    def test_init_with_imap_error(self, get_logger_mock, mock_imap_interface):
        mock_imap_interface.side_effect = imaplib.IMAP4.error

        with pytest.raises(imaplib.IMAP4.error):
            Imbox(hostname="hostname", username="user", password="pass")

        get_logger_mock.assert_called_once()

    @patch("logging.getLogger")
    def test_init_successful_connection(self, get_logger_mock, mock_imap_interface):
        Imbox(hostname="hostname", username="user", password="pass")

        get_logger_mock.assert_called_once()
        get_logger_mock().info.assert_called_once()
