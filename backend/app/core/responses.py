def success(data=None, **extra):
    """Every successful answer looks like {"data": ...}."""
    body = {"data": data}
    body.update(extra)
    return body
