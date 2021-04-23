def not_last_n(n, iterator):
    for i, element in enumerate(iterator):
        if len(iterator) - i > n:
            yield element
        else:
            raise StopIteration()


def format_error(err):
    msg = err.__class__.__name__ + "(" + str(err) + ")"
    if err.__cause__:
        msg += " caused by " + format_error(err.__cause__)
    return msg
