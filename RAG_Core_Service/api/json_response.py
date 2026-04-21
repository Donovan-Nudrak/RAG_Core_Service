#!/usr/bin/env python3

import json

from starlette.responses import JSONResponse


class UnicodeJSONResponse(JSONResponse):

    def render(self, content: object) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")
