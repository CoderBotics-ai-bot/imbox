import imaplib

from imbox.imap import ImapTransport
from imbox.messages import Messages

import logging

from imbox.vendors import GmailMessages, hostname_vendorname_dict, name_authentication_string_dict


from typing import Optional, Any


from typing import Dict, Any, Optional, Union, Type

logger = logging.getLogger(__name__)








class Imbox:

    def __init__(
        self,
        hostname: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        ssl: bool = True,
        port: Optional[int] = None,
        ssl_context: Optional[Any] = None,
        policy: Optional[Any] = None,
        starttls: bool = False,
        vendor: Optional[str] = None,
    ) -> None:
        """
        Initialize the Imbox class, connect to the IMAP server and prepare for handling exceptions.
        """
        self.connect_to_server(hostname, ssl, port, ssl_context, starttls)
        self.prepare_for_connection(username, password, policy, vendor)
        self.validate_and_establish_connection()

    def __enter__(self):
        return self

    def connect_to_server(self, hostname, ssl, port, ssl_context, starttls):
        self.server = ImapTransport(
            hostname, ssl=ssl, port=port, ssl_context=ssl_context, starttls=starttls
        )
        logger.info(
            f"Connected to IMAP Server with user {self.username} on {hostname}{' over SSL' if ssl or starttls else ''}"
        )

    def prepare_for_connection(self, username, password, policy, vendor):
        self.hostname = self.server.hostname
        self.username = username
        self.password = password
        self.parser_policy = policy
        self.vendor = vendor or hostname_vendorname_dict.get(self.hostname)

        if self.vendor is not None:
            self.authentication_error_message = name_authentication_string_dict.get(
                self.vendor
            )

    def validate_and_establish_connection(self):
        try:
            self.connection = self.server.connect(self.username, self.password)
        except imaplib.IMAP4.error as e:
            if self.authentication_error_message is not None:
                raise imaplib.IMAP4.error(
                    self.authentication_error_message + "\n" + str(e)
                )
            raise

    def __exit__(self, type, value, traceback):
        self.logout()

    def logout(self):
        self.connection.close()
        self.connection.logout()
        logger.info("Disconnected from IMAP Server {username}@{hostname}".format(
            hostname=self.hostname, username=self.username))

    def mark_seen(self, uid):
        logger.info("Mark UID {} with \\Seen FLAG".format(int(uid)))
        self.connection.uid('STORE', uid, '+FLAGS', '(\\Seen)')

    def mark_flag(self, uid):
        logger.info("Mark UID {} with \\Flagged FLAG".format(int(uid)))
        self.connection.uid('STORE', uid, '+FLAGS', '(\\Flagged)')

    def delete(self, uid):
        logger.info(
            "Mark UID {} with \\Deleted FLAG and expunge.".format(int(uid)))
        self.connection.uid('STORE', uid, '+FLAGS', '(\\Deleted)')
        self.connection.expunge()

    def messages(self, **kwargs: Any) -> ImapTransport:
        folder = self.extract_folder(kwargs)
        if folder is not None:
            kwargs.pop("folder")

        messages_class = self.select_message_class()

        if folder:
            self.connection.select(
                messages_class.FOLDER_LOOKUP.get(folder.lower(), folder)
            )
            msg = f" from folder '{folder}'"
        else:
            msg = " from inbox"

        logger.info(f"Fetch list of messages{msg}")

        return messages_class(
            connection=self.connection, parser_policy=self.parser_policy, **kwargs
        )

    def copy(self, uid, destination_folder):
        logger.info("Copy UID {} to {} folder".format(
            int(uid), str(destination_folder)))
        return self.connection.uid('COPY', uid, destination_folder)

    def extract_folder(self, kwargs: Dict[str, Any]) -> Optional[str]:
        """
        Extracts a folder keyword argument, if provided.

        Args:
            kwargs: A dict of keyword arguments.

        Returns:
            The value associated with 'folder' keyword argument, if it exists. None otherwise.
        """
        return kwargs.get("folder", None)

    def select_message_class(self) -> Type[Union[Messages, GmailMessages]]:
        """
        Selects the appropriate messages class based on the vendor.

        Returns:
            The selected class. GmailMessages if vendor is 'gmail', Messages otherwise.
        """
        return GmailMessages if self.vendor == "gmail" else Messages

    def move(self, uid, destination_folder):
        logger.info("Move UID {} to {} folder".format(
            int(uid), str(destination_folder)))
        if self.copy(uid, destination_folder):
            self.delete(uid)

    def folders(self):
        return self.connection.list()
