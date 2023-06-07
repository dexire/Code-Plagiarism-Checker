from pygments.lexers import CppLexer
from pygments.token import Token
import difflib
from io import StringIO
'''
Scores the similarities between two files.
'''
class FileScorer:
    def __init__(self):
        self.base_filepath = None
        self.normalized_base = None
        
    def replace_labels_with_elements(self, code):
        lexer = CppLexer()
        tokens = lexer.get_tokens(code)

        replaced_code = []
        for token_type, token_value in tokens:
            if token_type in Token.Name:
                replaced_code.append('<name>')
            elif token_type in Token.Keyword:
                replaced_code.append('<keyword>')
            else:
                replaced_code.append(token_value)

        return ''.join(replaced_code)
    
    def get_normalized_text_from_code(self, filepath):
        with open(filepath) as f:
            text = f.read()
            labelled_code = self.replace_labels_with_elements(text)
            normalized = StringIO(labelled_code).readlines()
            return normalized
        
        
    def score_for_files(self, filepath_other, filepath_base):
        normalized_other = self.get_normalized_text_from_code(filepath_other)
        
        if filepath_base != self.base_filepath:
            self.base_filepath = filepath_base
            self.normalized_base = self.get_normalized_text_from_code(filepath_base)
        
        sm = difflib.SequenceMatcher(None, normalized_other, self.normalized_base)
        score1 = sm.quick_ratio()
        sm = difflib.SequenceMatcher(None, self.normalized_base, normalized_other)
        score2 = sm.quick_ratio()
        
        return score1, score2