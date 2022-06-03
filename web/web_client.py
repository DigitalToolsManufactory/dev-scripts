from typing import Dict, List, Optional

import requests

from web.web_method import WebMethod
from web.web_response import WebResponse


class WebClient:

    def execute(self,
                method: WebMethod,
                url: str,
                parameters: Optional[Dict[str, str]] = None,
                body: Optional[str] = None,
                headers: Optional[Dict[str, List[str]]] = None) -> WebResponse:
        response: requests.Response = requests.request(method.name, url, parameters, body, headers)

        body: str = response.content.decode("UTF-8")
        headers: Dict[str, List[str]] = {key: [value] for key, value in response.headers}

        return WebResponse(
            response.status_code,
            body,
            headers
        )
