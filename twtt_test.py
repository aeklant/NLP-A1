import unittest
import twtt


class RemoveHTMLTest(unittest.TestCase):
    def test_remove_open_close_tags(self):
        self.assertEqual(twtt.remove_html("<html><head>title</head></html>"),
                         "title")

    def test_remove_only_close_tags(self):
        self.assertEqual(twtt.remove_html("title</html>"), "title")

    @unittest.expectedFailure
    def test_non_closed_tag(self):
        self.assertEqual(twtt.remove_html("<b class='forgot-to-close'"), "")

    @unittest.expectedFailure
    def test_non_tag(self):
        self.assertEqual(twtt.remove_html("if 3 < 5 then 5 > 3"), 
                         "if 3 < 5 then 5 > 3")

    def test_several_tags(self):
	self.assertEqual(twtt.remove_html("<body><b>body</b> here</body>"),
                         "body here")

    def test_ascii_conversion(self):
        self.assertEqual(twtt.remove_html("3 &#43; 1 = 4"),
                         "3 + 1 = 4")

    @unittest.expectedFailure
    def test_ascii_conversion_non_tag(self):
        self.assertEqual(twtt.remove_html("if 3 &#43; 1 < 5 then 5 > 3 + 1"),
                         "if 3 + 1 < 5 then 5 > 3 + 1")


class RemoveStartsWithTest(unittest.TestCase):
    def test_remove_http(self):
        self.assertEqual(twtt.remove_startswith("use http://google.com to search", 
                                                "http"),
                         "use  to search")

    def test_remove_http_beginning(self):
        self.assertEqual(twtt.remove_startswith("http://google.com for searching",
                                                "http"),
                         " for searching")

    def test_remove_http_end(self):
        self.assertEqual(twtt.remove_startswith("for searching: http://google.com",
                                                "http"),
                         "for searching: ")

    def test_remove_http_case_insensitive(self):
        self.assertEqual(twtt.remove_startswith("use HtTP://google.com to search",
                                                "http"),
                         "use  to search")

    def test_do_not_remove_http(self):
        self.assertEqual(twtt.remove_startswith("use googlehttp to search", 
                                                "http"),
                         "use googlehttp to search")

    def test_remove_www(self):
        self.assertEqual(twtt.remove_startswith("use www.google.com to search",
                                                "www"),
                         "use  to search")

    def test_remove_www_case_insensitive(self):
        self.assertEqual(twtt.remove_startswith("use WwW.gOOgle.com to search",
                                                "www"),
                         "use  to search")

    def test_do_not_remove_www(self):
        self.assertEqual(twtt.remove_startswith("awwwsome to search",
                                                "www"),
                         "awwwsome to search")

    def test_remove_at(self):
        self.assertEqual(twtt.remove_startswith("my username is @FTW",
                                                "@", remove_word=False),
                         "my username is FTW")
 
    def test_do_not_remove_at(self):
        self.assertEqual(twtt.remove_startswith("my email is ftw@ftw.com",
                                                "@", remove_word=False),
                         "my email is ftw@ftw.com")

    def test_remove_hashtag(self):
        self.assertEqual(twtt.remove_startswith("I like #turtles", "#", 
                                                remove_word=False),
                         "I like turtles")

    def test_do_not_remove_hashtag(self):
        self.assertEqual(twtt.remove_startswith("I like 2#turtles", "#",
                                                remove_word=False),
                         "I like 2#turtles")

class SeparateCliticsTest(unittest.TestCase):
    def test_clitics_separation(self):
        text = "Mr. Smith's dog doesn't chew on his own toy. Instead " \
               "he'll chew on other dogs' toys. I'd be careful if " \
               "I were you. You're a smart man; you've been warned. " \
               "I'm leaving now."

        res = "Mr. Smith 's dog does n't chew on his own toy. Instead " \
              "he 'll chew on other dogs ' toys. I 'd be careful if " \
              "I were you. You 're a smart man; you 've been warned. " \
              "I 'm leaving now."

        self.assertEqual(twtt.separate_clitics(text), res)


class SeparateSentencesTest(unittest.TestCase):
    def test_separate_sentences(self):
        text = "Mr. Potatohead drinks 2.2 liters of water a day, i.e. " \
               "he drinks a lot considering he weighs .3 grams. He is " \
               "of course, a potato. You don't believe me? I didn't " \
               "think so. Sure, I could be lying... You can always " \
               "look it up on google.com and see for yourself."

        res = ["Mr. Potatohead drinks 2.2 liters of water a day, i.e. " \
               "he drinks a lot considering he weighs .3 grams.",
               "He is of course, a potato.",
               "You don't believe me?",
               "I didn't think so.",
               "Sure, I could be lying...",
               "You can always look it up on google.com and see for " \
               "yourself."]
    
        self.assertEqual(twtt.separate_sentences(text), res)

if __name__ == "__main__":
    unittest.main()
