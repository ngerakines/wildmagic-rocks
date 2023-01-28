from string import Formatter
from typing import Dict, Any, Optional

import jinja2


class RecursiveFormatter(Formatter):
    def _contains_underformatted_field_names(self, format_tuple):
        literal_text, field_name, format_spec, conversion = format_tuple
        if field_name is not None:
            return any(component[1] is not None for component in self.parse(field_name))
        return False

    def _split_format_tuple(self, format_tuple):
        literal_text, field_name, format_spec, conversion = format_tuple

        yield (literal_text + "{", None, None, None)

        for format_tuple in self.parse(field_name):
            yield format_tuple

        literal_text = "".join(["" if not conversion else ("!" + conversion), "" if not format_spec else (":" + format_spec), "}"])

        yield (literal_text, None, None, None)

    def parse(self, format_string):
        def iter_tuples():
            for format_tuple in super(RecursiveFormatter, self).parse(format_string):
                if not self._contains_underformatted_field_names(format_tuple):
                    yield format_tuple
                else:
                    for subtuple in self._split_format_tuple(format_tuple):
                        yield subtuple

        return list(iter_tuples())

    def vformat(self, format_string, args, kwargs):
        while True:
            format_string = super(RecursiveFormatter, self).vformat(format_string, args, kwargs)

            # if any field_names remain uninterpolated
            if any(format_tuple[1] is not None for format_tuple in self.parse(format_string)):
                continue
            else:
                return format_string


from typing import Any, Dict, Optional, Union, TypedDict

import jinja2
from aiohttp import web
from yarl import URL


class _Context(TypedDict, total=False):
    app: web.Application


@jinja2.pass_context
def url_with_globals(context: _Context, __route_name: str, query_: Optional[Dict[str, str]] = None, **parts: Union[str, int]) -> URL:
    app = context["app"]

    query: Dict[str, str] = {}
    if "globals" in context:
        query.update(context["globals"])
    if query_ is not None:
        query.update(query_)

    parts_clean: Dict[str, str] = {}
    for key in parts:
        val = parts[key]
        if isinstance(val, str):
            val = str(val)
        elif type(val) is int:
            val = str(val)
        else:
            raise TypeError("argument value should be str or int, got {} -> [{}] {!r}".format(key, type(val), val))
        parts_clean[key] = val

    url = app.router[__route_name].url_for(**parts_clean)
    if len(query) > 0:
        url = url.with_query(query)
    return url
