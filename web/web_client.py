from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import requests

from utility.type_utility import get_or_else
from web.web_method import WebMethod
from web.web_response import WebResponse


class WebClient:

    def execute(self,
                method: WebMethod,
                url: str,
                parameters: Optional[Dict[str, str]] = None,
                authentication: Optional[Tuple[str, str]] = None,
                body: Optional[str] = None,
                headers: Optional[Dict[str, List[str]]] = None,
                verify: Optional[Union[bool, Path]] = None) -> WebResponse:
        response: requests.Response = requests.request(
            method=method.name,
            url=url,
            params=parameters,
            data=body,
            headers=headers,
            auth=authentication,
            verify=get_or_else(verify, True)
        )

        body: str = response.content.decode("UTF-8")
        headers: Dict[str, List[str]] = {key: [value] for key, value in response.headers}

        return WebResponse(
            response.status_code,
            body,
            headers
        )
