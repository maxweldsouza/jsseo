def print_if_false(f):
    def wrapper(*args):
        result = f(*args)
        if not result:
            if __name__ != '__main__':
                print args
        return result
    return wrapper

@print_if_false
def compare_dicts(expected, actual):
    for key in expected:
        if not key in actual:
            return False
        if not compare(expected[key], actual[key]):
            return False
    return True

@print_if_false
def compare_lists(expected, actual):
    if len(expected) != len(actual):
        return False
    for i, value in enumerate(expected):
        if not compare(value, actual[i]):
            return False
    return True

@print_if_false
def compare(expected, actual):
    if type(expected) != type(actual):
        return False
    if isinstance(expected, dict):
        return compare_dicts(expected, actual)
    elif isinstance(expected, list):
        return compare_lists(expected, actual)
    else:
        return expected == actual

    return True

assert(not compare([], 1))
assert(compare(1, 1))
assert(compare({}, {}))
assert(compare_dicts({"key": "value"}, {"key": "value"}))
assert(not compare_dicts({"key": "value"}, {"key": "value2"}))
assert(not compare_dicts({"key": {"key": "value"}}, {"key": "value"}))
assert(compare({"key": "value"}, {"key": "value"}))
assert(not compare({"key": "value"}, {"key": "value2"}))
assert(not compare({"key": {"key": "value"}}, {"key": "value"}))
assert(compare_lists([], []))
assert(compare_lists([1, 2], [1, 2]))
assert(not compare_lists([1, 2, 3], [1, 2]))
assert(not compare_lists([1, 2], [1, 3]))

