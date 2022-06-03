from unittest import TestCase

from __test__.matcher import Matcher
from __test__.string_matcher import StringMatcher
from __test__.web.mock.mock_web_client import MockWebClient
from web.web_method import WebMethod
from web.web_response import WebResponse


class TestMockWebClient(TestCase):
    def test_execute_any_request(self) -> None:
        mock: MockWebClient = MockWebClient()

        mock.when_request()\
            .has_method(Matcher.any())\
            .has_url(StringMatcher.any())\
            .then_return(WebResponse.ok("I was mocked!"))

        response: WebResponse = mock.execute(WebMethod.GET, "https://foo.bar")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_okay())
        self.assertEqual(response.body, "I was mocked!")
        self.assertDictEqual(response.headers, {})
