from dataclasses import dataclass
from typing import Optional, Dict, List

from __test__.dict_matcher import DictMatcher
from __test__.matcher import Matcher
from __test__.string_matcher import StringMatcher
from web.web_client import WebClient
from web.web_method import WebMethod
from web.web_response import WebResponse


@dataclass(frozen=True)
class MockWebRequestInvocation:
    method: WebMethod
    url: str
    parameters: Optional[Dict[str, str]] = None
    body: Optional[str] = None
    headers: Optional[Dict[str, List[str]]] = None


@dataclass(frozen=True)
class MockWebRequestInvocationMatcher:
    method_matcher: Optional[Matcher[WebMethod]] = None
    url_matcher: Optional[StringMatcher] = None
    parameter_matchers: Optional[List[DictMatcher[str, str]]] = None
    body_matcher: Optional[StringMatcher] = None
    header_matchers: Optional[List[DictMatcher[str, List[str]]]] = None

    def matches(self, invocation: MockWebRequestInvocation) -> bool:
        result: bool = True

        if self.method_matcher is not None:
            result &= self.method_matcher.matches(invocation.method)

        if self.url_matcher is not None:
            result &= self.url_matcher.matches(invocation.url)

        if self.parameter_matchers is not None:
            for matcher in self.parameter_matchers:
                result &= matcher.matches(invocation.parameters)

        if self.body_matcher is not None:
            result &= self.body_matcher.matches(invocation.body)

        if self.header_matchers is not None:
            for matcher in self.header_matchers:
                result &= matcher.matches(invocation.headers)

        return result


@dataclass(frozen=True)
class MockWebRequestRule:
    invocation_matcher: MockWebRequestInvocationMatcher
    response: WebResponse

    def matches(self, invocation: MockWebRequestInvocation) -> bool:
        return self.invocation_matcher.matches(invocation)


class MockWebClient(WebClient):

    def __init__(self):
        self._mock_rules: List[MockWebRequestRule] = []

    def execute(self,
                method: WebMethod,
                url: str,
                parameters: Optional[Dict[str, str]] = None,
                body: Optional[str] = None,
                headers: Optional[Dict[str, List[str]]] = None) -> WebResponse:
        invocation: MockWebRequestInvocation = MockWebRequestInvocation(
            method,
            url,
            parameters,
            body,
            headers
        )

        for rule in self._mock_rules:
            if rule.matches(invocation):
                return rule.response

        raise AssertionError(
            f"No rule specified that matches the following request: {method} {url} {parameters} {body} {headers}")

    # region MockRule builder
    def when_method(self, matcher: Matcher[WebMethod]) -> "MockWebClient.UrlMatcherBuilder":
        return MockWebClient.UrlMatcherBuilder(self, matcher)

    class UrlMatcherBuilder:
        def __init__(self,
                     mock_client: "MockWebClient",
                     method_matcher: Optional[Matcher[WebMethod]] = None):
            self._mock_client: MockWebClient = mock_client
            self._method_matcher: Optional[Matcher[WebMethod]] = method_matcher

        def on_url(self, url_matcher: StringMatcher) -> "MockWebClient.UrlParametersMatcherBuilder":
            return MockWebClient.UrlParametersMatcherBuilder(
                self._mock_client,
                self._method_matcher,
                url_matcher
            )

    class UrlParametersMatcherBuilder:
        def __init__(self,
                     mock_client: "MockWebClient",
                     method_matcher: Optional[Matcher[WebMethod]] = None,
                     url_matcher: Optional[StringMatcher] = None):
            self._mock_client: MockWebClient = mock_client
            self._method_matcher: Optional[Matcher[WebMethod]] = method_matcher
            self._url_matcher: Optional[StringMatcher] = url_matcher
            self._parameter_matchers: List[DictMatcher[str, str]] = []
            self._header_matchers: List[DictMatcher[str, List[str]]] = []

        def has_parameter(self,
                          parameter_matcher: DictMatcher[str, str]) -> "MockWebClient.UrlParametersMatcherBuilder":
            self._parameter_matchers.append(parameter_matcher)
            return self

        def has_header(self,
                       header_matcher: DictMatcher[str, List[str]]) -> "MockWebClient.UrlParametersMatcherBuilder":
            self._header_matchers.append(header_matcher)
            return self

        def has_body(self, body_matcher: StringMatcher) -> "MockWebClient.FinalBuilder":
            return MockWebClient.FinalBuilder(
                self._mock_client,
                self._method_matcher,
                self._url_matcher,
                self._parameter_matchers,
                body_matcher
            )

        def then_respond(self, response: WebResponse) -> None:
            invocation_matcher: MockWebRequestInvocationMatcher = MockWebRequestInvocationMatcher(
                self._method_matcher,
                self._url_matcher,
                self._parameter_matchers,
                StringMatcher.any(),
                self._header_matchers
            )
            rule: MockWebRequestRule = MockWebRequestRule(invocation_matcher, response)

            self._mock_client._mock_rules.append(rule)

    class FinalBuilder:
        def __init__(self,
                     mock_client: "MockWebClient",
                     method_matcher: Optional[Matcher[WebMethod]] = None,
                     url_matcher: Optional[StringMatcher] = None,
                     parameter_matchers: Optional[List[DictMatcher[str, str]]] = None,
                     body_matcher: Optional[StringMatcher] = None,
                     header_matchers: Optional[List[DictMatcher[str, List[str]]]] = None):
            self._mock_client: MockWebClient = mock_client
            self._method_matcher: Optional[Matcher[WebMethod]] = method_matcher
            self._url_matcher: Optional[StringMatcher] = url_matcher
            self._parameter_matchers: List[DictMatcher[str, str]] = parameter_matchers
            self._body_matcher: Optional[StringMatcher] = body_matcher
            self._header_matchers: Optional[List[DictMatcher[str, List[str]]]] = header_matchers

        def then_respond(self, response: WebResponse) -> None:
            invocation_matcher: MockWebRequestInvocationMatcher = MockWebRequestInvocationMatcher(
                self._method_matcher,
                self._url_matcher,
                self._parameter_matchers,
                self._body_matcher,
                self._header_matchers
            )
            rule: MockWebRequestRule = MockWebRequestRule(invocation_matcher, response)

            self._mock_client._mock_rules.append(rule)

    # endregion
