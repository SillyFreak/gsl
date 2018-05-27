import re


def case(*, to, **kwargs):
    """Converts an identifier from one case type to another.
    An identifier is an ASCII string consisting of letters, digits and underscores, not starting with a digit.
    The supported case types are camelCase, PascalCase, snake_case, and CONSTANT_CASE,
    identified as camel, pascal, snake, and constant.
    The input identifier is given as a keyword argument with one of these names,
    and the output type is given as a string in the `to` keyword argument.
    If a given string does not conform to the specified case type (such as underscores in camel or pascal case strings,
    or double__underscores in general), the result may not be as desired,
    although things like snaKe_casE or CONStaNT_CASe will generally work."""

    if len(kwargs) != 1:
        raise ValueError("expect exactly one source string argument")

    [(typ, string)] = kwargs.items()

    types = {'pascal', 'camel', 'snake', 'constant'}
    if typ not in types:
        raise ValueError(f"source string keyword must be one of {types}")
    if to not in types:
        raise ValueError(f"\"to\" argument must be one of {types}")

    def pascal_iter(string):
        yield from (m.group(0) for m in re.finditer(r'[A-Z][a-z0-9]*|[a-z0-9]+', string))

    def snake_iter(string):
        yield from (m.group(2) for m in re.finditer(r'(^|_)([A-Za-z0-9]+)', string))

    inputs = {
        'pascal': pascal_iter,
        'camel': pascal_iter,
        'snake': snake_iter,
        'constant': snake_iter,
    }

    def out_fun(sep, case=None, case_fst=None):
        if case is None:
            case = lambda x: x
        if case_fst is None:
            case_fst = case
        return lambda tokens: sep.join(case_fst(token) if i == 0 else case(token) for i, token in enumerate(tokens))

    outputs = {
        'pascal': out_fun('', str.capitalize),
        'camel': out_fun('', str.capitalize, str.lower),
        'snake': out_fun('_', str.lower),
        'constant': out_fun('_', str.upper),
    }

    tokens = inputs[typ](string)
    return outputs[to](tokens)
