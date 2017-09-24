class FullTextMatcher:

    def match(self, string, strings):
        return string in strings

class PatternMatcher:

    def match(self, string, strings):
        return string in strings;
