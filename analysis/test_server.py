import unittest

from jsonschema import validate, ValidationError

import server
import schema

class TestAnalysisFunctions(unittest.TestCase):

    def setUp(self):
        self.angry_text = "I am just so displeased with the current situation!"
        self.nice_two_sentences = "This is so great! I just love writing code on GitHub!"
        self.dirty_text = """Check out `cool.py`:
        ```
        def funk(**cool_args):
            if "bro" in cool_args.keys():
                return "bruh"
            else:
                return "meh"
        ```
        Isn't it just so great!"""

        self.clean_text ="""Check out cool.py:
        Isn't it just so great!"""

    def test_error_on_none(self):
        analysis_result = server.sentiment_analysis(None)
        self.assertTrue("error" in analysis_result.keys())

    def test_valid_with_empty(self):
        analysis_result = server.sentiment_analysis("")
        validate(analysis_result, schema.SENTIMENT)

    def test_single_text(self):
        analysis_result = server.sentiment_analysis(self.angry_text)
        self.assertTrue(analysis_result["analyzed_text"] == self.angry_text)
        validate(analysis_result, schema.SENTIMENT)

    def test_multiple_sentences(self):
        analysis_result = server.sentiment_analysis(self.nice_two_sentences)
        self.assertTrue(analysis_result["analyzed_text"] == self.nice_two_sentences)
        self.assertTrue(len(analysis_result["breakdown"]) == 2)
        validate(analysis_result, schema.SENTIMENT)

    def test_dirty_text(self):
        analysis_result = server.sentiment_analysis(self.dirty_text)
        self.assertTrue(analysis_result["analyzed_text"] == self.clean_text)
        validate(analysis_result, schema.SENTIMENT)

if __name__ == '__main__':
    unittest.main(verbosity=2)
