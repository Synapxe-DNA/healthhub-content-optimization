def merge_dict(dict1: dict, dict2: dict) -> dict:
    # Iterate through the items in dict1
    for key, val in dict1.items():
        # Check if the value is a dictionary
        if isinstance(val, dict):
            # Recursively merge if the key exists in dict2 and the corresponding value is a dictionary
            if key in dict2 and type(dict2[key] == dict):
                merge_dict(dict1[key], dict2[key])
        else:
            # Assign the value from dict2 to dict1 if key exists
            if key in dict2:
                dict1[key] = dict2[key]

    # Add key-value pairs in dict2 that are not in dict1
    for key, val in dict2.items():
        if key not in dict1:
            dict1[key] = val

    return dict1
