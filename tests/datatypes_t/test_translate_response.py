from unittest import TestCase

from datatypes.translate_response import TranslateResponse, current_version


class TestTranslateResponse(TestCase):

    def test_current_version(self):
        response = TranslateResponse(version=current_version, html="some_html")
        parsed = TranslateResponse.parse(response.model_dump())
        self.assertIsNotNone(parsed)
        self.assertEqual(response, parsed)

    def test_parse_missed_version(self):
        response = TranslateResponse(version=current_version, html="some_html")
        response_dict = response.model_dump()
        response_dict.pop("version")
        parsed = TranslateResponse.parse(response_dict)
        self.assertIsNone(parsed)

    def test_parse_old_version(self):
        response = TranslateResponse(version=current_version, html="some_html")
        response_dict = response.model_dump()
        response_dict["version"] = "old_version"
        parsed = TranslateResponse.parse(response_dict)
        self.assertIsNone(parsed)
