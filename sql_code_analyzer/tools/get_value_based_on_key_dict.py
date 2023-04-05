
def get_value_based_on_key_dict(d, v):
    for key, value in d.items():
        if v == value:
            return key
    return None
