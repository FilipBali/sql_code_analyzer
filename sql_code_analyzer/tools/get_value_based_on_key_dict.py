
def get_value_based_on_key_dict(d, v):
    """
    Returns key based on value if exists
    :param d: Dictionary
    :param v: Value
    :return: Key or None
    """

    for key, value in d.items():
        if v == value:
            return key
    return None
