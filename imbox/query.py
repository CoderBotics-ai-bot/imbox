import datetime

from imbox.utils import date_to_date_text


from typing import Dict, Any


def build_search_query(imap_attribute_lookup: dict, **kwargs: str) -> str:
    """Constructs the search query for IMAP server.

    Parameters:
    imap_attribute_lookup (dict): The dictionary containing attribute mappings.
    **kwargs (str): Various keyword arguments representing the attributes to search.

    The function processes `kwargs` where each keyword argument generates an IMAP query component. These components are joined together with space characters to create the final IMAP query. If `kwargs` are empty or none of the attributes have been specified, the function returns '(ALL)'.

    Values that are instances of `datetime.date` are converted to strings. If a string contains a double quote character ('"'), it is replaced by a single quote character ("'").

    Returns:
    str: The final IMAP search query.
    """
    query = [
        imap_attribute_lookup[name].format(handle_value(value))
        for name, value in kwargs.items()
        if value is not None
    ]

    if query:
        return " ".join(query)

    return "(ALL)"



def handle_value(value: Any) -> str:
    """Extract the correct value for IMAP search.

    Depending on the type and content of the value, make necessary adjustments
    for IMAP search, such as date conversion and quote replacements.

    Parameters:
    value (Any): The raw value to be adjusted.

    Returns:
    str: Value adjusted for IMAP search.
    """
    if isinstance(value, datetime.date):
        value = date_to_date_text(value)
    elif '"' in str(value):
        value = str(value).replace('"', "'")
    return str(value)
