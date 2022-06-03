from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Callable

import requests

from utility.type_utility import get_or_else
from web.web_method import WebMethod
from web.web_response import WebResponse


class DefaultWebClient:

    @staticmethod
    def new() -> "WebClient":
        return WebClient()

    def __init__(self):
        raise AssertionError("This utility class must not be instantiated.")


class WebClient:

    def execute_or_raise(self,
                         method: WebMethod,
                         url: str,
                         parameters: Optional[Dict[str, str]] = None,
                         authentication: Optional[Tuple[str, str]] = None,
                         body: Optional[str] = None,
                         headers: Optional[Dict[str, List[str]]] = None,
                         verify: Optional[Union[bool, Path]] = None,
                         exception: Optional[
                             Union[Exception, Callable[[WebResponse], Exception]]] = None) -> WebResponse:
        response: WebResponse = self.execute(method, url, parameters, authentication, body, headers, verify)

        if response.is_okay():
            return response

        if exception is None:
            raise Exception(f"The request '{method.name} {url}' returned {response.status_code}:\n"
                            f"body:\n'{response.body}'\n"
                            f"headers:\n'{response.headers}'")

        if isinstance(exception, Exception):
            raise exception

        raise exception(response)

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
            headers=self._create_request_headers(headers),
            auth=authentication,
            verify=get_or_else(verify, True)
        )

        body: str = response.content.decode("UTF-8")
        headers: Dict[str, List[str]] = {key: [value] for key, value in response.headers.items()}

        return WebResponse(
            response.status_code,
            body,
            headers
        )

    def _create_request_headers(self, headers: Optional[Dict[str, List[str]]]) -> Dict[str, str]:
        if headers is None:
            return {}

        result: Dict[str, str] = {}
        for key, values in headers.items():
            if key.lower() == "set-cookie":
                result[key] = ";".join(values)

            else:
                result[key] = ",".join(values)

        return result
