import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from utility.type_utility import get_or_else


@dataclass(frozen=True)
class WebResponse:
    status_code: int
    body: str = ""
    headers: Dict[str, List[str]] = field(default_factory=Dict)

    def is_okay(self) -> bool:
        return 200 <= self.status_code < 300

    def body_as_json(self) -> Optional[Dict[str, Any]]:
        try:
            return json.loads(self.body)

        except:
            return None

    @staticmethod
    def ok(
        body: Optional[str] = None, headers: Optional[Dict[str, List[str]]] = None
    ) -> "WebResponse":
        return WebResponse(200, get_or_else(body, ""), get_or_else(headers, {}))

    @staticmethod
    def client_error(
        body: Optional[str] = None, headers: Optional[Dict[str, List[str]]] = None
    ) -> "WebResponse":
        return WebResponse(400, get_or_else(body, ""), get_or_else(headers, {}))

    @staticmethod
    def server_error(
        body: Optional[str] = None, headers: Optional[Dict[str, List[str]]] = None
    ) -> "WebResponse":
        return WebResponse(500, get_or_else(body, ""), get_or_else(headers, {}))
