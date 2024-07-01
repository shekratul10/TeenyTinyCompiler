import enum
import sys

class Lexer:
    def __init__(self, source):
        self.source = source + '\n'
        self.curr_char= ''
        self.curr_pos = -1
        self.next_char()

    def next_char(self):
        self.curr_pos += 1
        if self.curr_pos >= len(self.source):
            self.curr_char = '\0'
        else:
            self.curr_char = self.source[self.curr_pos]

    def peek(self):
        if self.curr_pos + 1 >= len(self.source):
            return '\0'
        else:
            return self.source[self.curr_pos+1]

    def skip_whitespaces(self):
        while self.curr_char == ' ' or self.curr_char == '\t' or self.curr_char == '\r':
            self.next_char()

    def skip_comment(self):
        if self.curr_char == '#':
            while self.curr_char != '\n':
                self.next_char()

    def get_token(self):
        self.skip_whitespaces()
        self.skip_comment()
        token = None

        if self.curr_char == '+':
            token = Token(self.curr_char, TokenType.PLUS)

        elif self.curr_char == '-':
            token = Token(self.curr_char, TokenType.MINUS)

        elif self.curr_char == '*':
            token = Token(self.curr_char, TokenType.ASTERISK)

        elif self.curr_char == '/':
            token = Token(self.curr_char, TokenType.SLASH)

        elif self.curr_char == '=':
            if self.peek() =='=':
                last_char = self.curr_char
                self.next_char()
                token = Token(last_char + self.curr_char, TokenType.EQEQ)
            else:
                token = Token(self.curr_char, TokenType.EQ)

        elif self.curr_char == '>':
            if self.peek() == '=':
                last_char = self.curr_char
                self.next_char()
                token = Token(last_char + self.curr_char, TokenType.GTEQ)
            else:
                token = Token(self.curr_char, TokenType.GT)

        elif self.curr_char == '<':
            if self.peek() == '=':
                last_char = self.curr_char
                self.next_char()
                token = Token(last_char + self.curr_char, TokenType.LTEQ)
            else:
                token = Token(self.curr_char, TokenType.LT)

        elif self.curr_char == '!':
            if self.peek() == '=':
                last_char = self.curr_char
                self.next_char()
                token = Token(last_char + self.curr_char, TokenType.NOTEQ)
            else:
                self.abort("Expected !=, got: !" + self.peek())

        elif self.curr_char == '\"':
            self.next_char()
            start_pos = self.curr_pos

            while self.curr_char != '\"':
                if self.curr_char == '\r' or self.curr_char == '\n' or self.curr_char == '\t' or self.curr_char == '\\' or self.curr_char == '%':
                    self.abort("Illegal character in string!")
                self.next_char()

            token_text = self.source[start_pos:self.curr_pos]
            token = Token(token_text, TokenType.STRING)

        elif self.curr_char.isdigit():
            start_pos = self.curr_pos
            while self.peek().isdigit():
                self.next_char()
            if self.peek() == '.':
                self.next_char()

                if not self.peek().isdigit():
                    self.abort("Illegal character in number: " + self.peek())
                while self.peek().isdigit():
                    self.next_char()
            token_text= self.source[start_pos : self.curr_pos+1]
            token = Token(token_text, TokenType.NUMBER)
        
        elif self.curr_char.isalpha():
            start_pos = self.curr_pos
            while self.curr_char.isalnum():
                self.next_char()
            
            token_text = self.source[start_pos : self.curr_pos]
            keyword = Token.check_if_keyword(token_text)
            if keyword == None:
                token = Token(token_text, TokenType.IDENT)
            else:
                token = Token(token_text, keyword)

        elif self.curr_char == '\n':
            token = Token(self.curr_char, TokenType.NEWLINE)

        elif self.curr_char == '\0':
            token = Token('', TokenType.EOF)

        else:
            self.abort("Unkown token: " + self.curr_char)

        self.next_char()
        return token
    
    def abort(self, message):
        sys.exit("Lexing error. " + message)

class Token:
    def __init__(self, token_text, token_kind):
        self.text = token_text
        self.kind = token_kind

    @staticmethod
    def check_if_keyword(token_text):
        for kind in TokenType:
            if kind.name == token_text and kind.value >=100 and kind.value < 200:
                return kind
        return None

class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3

    LABEL = 101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107
    ENDIF = 108
    WHILE = 109
    REPEAT = 110
    ENDWHILE = 111

    EQ = 201
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211