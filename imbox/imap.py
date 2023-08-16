from imaplib import IMAP4, IMAP4_SSL

import logging
import ssl as pythonssllib


from typing import Optional

logger = logging.getLogger(__name__)




class ImapTransport:

    def __init__(
        self,
        hostname: str,
        port: Optional[int] = None,
        ssl: bool = True,
        ssl_context: Optional[pythonssllib.SSLContext] = None,
        starttls: bool = False,
    ) -> None:
        self.hostname = hostname
        self.port = port or (993 if ssl else 143)
        self.ssl_context = ssl_context or pythonssllib.create_default_context()

        self._create_server(ssl)
        if starttls:
            self.server.starttls()

        logger.debug(f"Created IMAP4 transport for {self.hostname}:{self.port}")

    def list_folders(self):
        logger.debug("List all folders in mailbox")
        return self.server.list()

    def _create_server(self, ssl: bool) -> None:
        server_class = IMAP4_SSL if ssl else IMAP4
        self.server = server_class(
            self.hostname, self.port, ssl_context=self.ssl_context
        )

    def connect(self, username, password):
        self.server.login(username, password)
        self.server.select()
        logger.debug("Logged into server {} and selected mailbox 'INBOX'"
                     .format(self.hostname))
        return self.server
