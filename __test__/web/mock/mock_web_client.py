from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Union

from __test__.dict_matcher import DictMatcher
from __test__.matcher import Matcher
from __test__.string_matcher import StringMatcher
from __test__.tuple_matcher import TupleMatcher
from web.web_client import WebClient
from web.web_method import WebMethod
from web.web_response import WebResponse


@dataclass(frozen=True)
class MockWebRequestInvocation:
    method: WebMethod
    url: str
    parameters: Optional[Dict[str, str]] = None
    authentication: Optional[Tuple[str, str]] = None
    body: Optional[str] = None
    headers: Optional[Dict[str, List[str]]] = None
    verify: Optional[Union[bool, Path]] = None


@dataclass(frozen=True)
class MockWebRequestInvocationMatcher:
    method_matcher: Optional[Matcher[WebMethod]] = None
    url_matcher: Optional[StringMatcher] = None
    parameter_matchers: Optional[List[DictMatcher[str, str]]] = None
    authentication_matcher: Optional[TupleMatcher[str, str]] = None
    body_matcher: Optional[StringMatcher] = None
    header_matchers: Optional[List[DictMatcher[str, List[str]]]] = None
    verify_matcher: Matcher[Union[bool, Path]] = None

    def matches(self, invocation: MockWebRequestInvocation) -> bool:
        result: bool = True

        if self.method_matcher is not None:
            result &= self.method_matcher.matches(invocation.method)

        if self.url_matcher is not None:
            result &= self.url_matcher.matches(invocation.url)

        if self.parameter_matchers is not None:
            for matcher in self.parameter_matchers:
                result &= matcher.matches(invocation.parameters)

        if self.authentication_matcher is not None:
            result &= self.authentication_matcher.matches(invocation.authentication)

        if self.body_matcher is not None:
            result &= self.body_matcher.matches(invocation.body)

        if self.header_matchers is not None:
            for matcher in self.header_matchers:
                result &= matcher.matches(invocation.headers)

        if self.verify_matcher is not None:
            result &= self.verify_matcher.matches(invocation.verify)

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
                authentication: Optional[Tuple[str, str]] = None,
                body: Optional[str] = None,
                headers: Optional[Dict[str, List[str]]] = None,
                verify: Optional[Union[bool, Path]] = None) -> WebResponse:
        invocation: MockWebRequestInvocation = MockWebRequestInvocation(
            method,
            url,
            parameters,
            authentication,
            body,
            headers,
            verify
        )

        for rule in self._mock_rules:
            if rule.matches(invocation):
                return rule.response

        raise AssertionError(
            f"No rule specified that matches the following request: {method} {url} {parameters} {body} {headers}")

    def when_request(self) -> "MockWebClient.RuleBuilderStep1":
        return MockWebClient.RuleBuilderStep1(self)

    class RuleBuilderStep1:
        def __init__(self, mock_client: "MockWebClient"):
            self._mock_client: MockWebClient = mock_client

        def has_method(self, matcher: Optional[Matcher[WebMethod]]) -> "MockWebClient.RuleBuilderStep2":
            return MockWebClient.RuleBuilderStep2(
                self._mock_client,
                matcher
            )

    class RuleBuilderStep2:
        def __init__(self,
                     mock_client: "MockWebClient",
                     method_matcher: Optional[Matcher[WebMethod]]):
            self._mock_client: MockWebClient = mock_client
            self._method_matcher: Optional[Matcher[WebMethod]] = method_matcher

        def has_url(self, matcher: Optional[StringMatcher]) -> "MockWebClient.RuleBuilderStep3":
            return MockWebClient.RuleBuilderStep3(
                self._mock_client,
                self._method_matcher,
                matcher
            )

    class RuleBuilderStep3:
        def __init__(self,
                     mock_client: "MockWebClient",
                     method_matcher: Optional[Matcher[WebMethod]],
                     url_matcher: Optional[StringMatcher]):
            self._mock_client: MockWebClient = mock_client
            self._method_matcher: Optional[Matcher[WebMethod]] = method_matcher
            self._url_matcher: Optional[StringMatcher] = url_matcher
            self._parameter_matchers: List[DictMatcher[str, str]] = []
            self._authentication_matcher: Optional[TupleMatcher[str, str]] = None
            self._body_matcher: Optional[StringMatcher] = None
            self._header_matchers: List[DictMatcher[str, List[str]]] = []
            self._verify_matcher: Optional[Matcher[Union[bool, Path]]] = None

        def has_parameter(self, matcher: DictMatcher[str, str]) -> "MockWebClient.RuleBuilderStep3":
            self._parameter_matchers.append(matcher)
            return self

        def has_authentication(self, matcher: Optional[TupleMatcher[str, str]]) -> "MockWebClient.RuleBuilderStep3":
            self._authentication_matcher = matcher
            return self

        def has_body(self, matcher: Optional[StringMatcher]) -> "MockWebClient.RuleBuilderStep3":
            self._body_matcher = matcher
            return self

        def has_header(self, matcher: DictMatcher[str, List[str]]) -> "MockWebClient.RuleBuilderStep3":
            self._header_matchers.append(matcher)
            return self

        def has_verify(self, matcher: Matcher[Union[bool, Path]]) -> "MockWebClient.RuleBuilderStep3":
            self._verify_matcher = matcher
            return self

        def then_return(self, response: WebResponse) -> None:
            matcher: MockWebRequestInvocationMatcher = MockWebRequestInvocationMatcher(
                self._method_matcher,
                self._url_matcher,
                self._parameter_matchers,
                self._authentication_matcher,
                self._body_matcher,
                self._header_matchers,
                self._verify_matcher
            )

            rule: MockWebRequestRule = MockWebRequestRule(matcher, response)
            self._mock_client._mock_rules.append(rule)
