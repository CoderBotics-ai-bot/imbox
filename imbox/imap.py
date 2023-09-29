from imaplib import IMAP4, IMAP4_SSL

import logging
import ssl as pythonssllib


from typing import Optional

logger = logging.getLogger(__name__)








class ImapTransport:

    def __init__(
        self, host: str, port: int = 993, ssl: bool = True, certs: Optional[str] = None
    ) -> None:
        """Initialize ImapTransport instance.

        Args:
            host (str): The host name.
            port (int, optional): The port number, defaults to 993.
            ssl (bool, optional): Use SSL or not, defaults to True.
            certs (Optional[str], optional): SSL certificate path, defaults to None.
        """
        self.host = host
        self.port = port
        self.ssl = ssl
        self.certs = certs
        self.mailbox = None
        self.connected = False

        if self.ssl:
            self.init_ssl_context()
        else:
            self.mail_server = IMAP4(self.host, self.port)

    def list_folders(self):
        logger.debug("List all folders in mailbox")
        return self.server.list()

    def init_ssl_context(self) -> None:
        """Initialize SSL context."""
        if self.certs:
            self.ssl_context = pythonssllib.create_default_context(
                pythonssllib.Purpose.CLIENT_AUTH, cafile=self.certs
            )
            self.mail_server = IMAP4_SSL(
                self.host, self.port, ssl_context=self.ssl_context
            )
        else:
            self.mail_server = IMAP4_SSL(self.host, self.port)

    def connect(self, username, password):
        self.server.login(username, password)
        self.server.select()
        logger.debug("Logged into server {} and selected mailbox 'INBOX'"
                     .format(self.hostname))
        return self.server
