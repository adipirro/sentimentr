import unittest

import server

class TestAnalysisFunctions(unittest.TestCase):

    def setUp(self):
        self.basic_object = {
            'analyzed_text': "",
            'polarity': 0,
            'subjectivity': 0,
            'breakdown': []
        }
        self.text_with_code_block = "blah blah blah\n```\r\nsome code\r\n some more code\r\n```\nblah blah blah"
        self.code_cleaned = "blah blah blah\nblah blah blah"

        self.text_with_inline_code = "blah blah blah check out `cool.txt` it is almost better than `funk.py`"
        self.inline_cleaned = "blah blah blah check out  it is almost better than "

    def test_basic_on_none(self):
        analysis_result = server.sentiment_analysis(None)
        self.assertEqual(analysis_result, self.basic_object)

    def test_basic_with_empty(self):
        analysis_result = server.sentiment_analysis("")
        self.assertEqual(analysis_result, self.basic_object)

    def test_dirty_code_block(self):
        actual = server.clean_text(self.text_with_code_block)
        self.assertEqual(actual, self.code_cleaned)

    def test_dirty_inline_code(self):
        actual = server.clean_text(self.text_with_inline_code)
        self.assertEqual(actual, self.inline_cleaned)

    def test_extra_dirty_combo(self):
        actual = server.clean_text(self.text_with_inline_code + self.text_with_code_block)
        self.assertEqual(actual, self.inline_cleaned + self.code_cleaned)

if __name__ == '__main__':
    unittest.main(verbosity=2)
