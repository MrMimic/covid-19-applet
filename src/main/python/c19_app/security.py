#!/usr/bin/env python3

import json

from flask import escape


def detect_json(string):
    """ Simple security """
    try:
        json.loads(string)
        return True
    except (ValueError, json.decoder.JSONDecodeError):
        return False


def validate_query(user_query):
    """ Simple security """
    # Ensure requets
    user_query = escape(user_query)
    # Keep out json
    if detect_json(user_query) is True:
        return None, "JSON-like queries are not allowed."

    return user_query, "Query validated."
