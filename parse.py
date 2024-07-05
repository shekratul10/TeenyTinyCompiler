import sys
from lex import *
from emit import *

class Parser:
    def __init__(self, lexer, emitter):
        self.lexer = lexer
        self.emitter = emitter

        self.symbols = set()
        self.labels_declared = set()
        self.labels_gotoed = set()

        self.curr_token = None
        self.peek_token = None
        self.next_token()
        self.next_token()
    
    def check_token(self, kind):
        return kind == self.curr_token.kind

    def check_peek(self, kind):
        return kind == self.peek_token.kind

    def match(self, kind):
        if not self.check_token(kind):
            self.abort("Expected " + kind.name + ", got " + self.curr_token.kind.name )
        self.next_token()

    def next_token(self):
        self.curr_token = self.peek_token
        self.peek_token = self.lexer.get_token()

    def abort(self, message):
        sys.exit("Error: " + message)
    
    def is_comparison_operator(self):
        return self.check_token(TokenType.EQEQ) or self.check_token(TokenType.NOTEQ) or self.check_token(TokenType.GT) or self.check_token(TokenType.GTEQ) or self.check_token(TokenType.LT) or self.check_token(TokenType.LTEQ)
    
    # program ::= {statement}
    def program(self):
        
        self.emitter.header_line("#include <stdio.h>")
        self.emitter.header_line("int main(void){")

        while(self.check_token(TokenType.NEWLINE)):
            self.next_token()
        
        while not self.check_token(TokenType.EOF):
            self.statement()
        
        self.emitter.emit_line("return 0;")
        self.emitter.emit_line("}")
        
        for label in self.labels_gotoed:
            if label not in self.labels_declared:
                self.abort("Attempting to GOTO to undeclared label: " + label)
    
    # statement ::= "PRINT" (expression | string) nl
    # | "IF" comparison "THEN" nl {statement} "ENDIF" nl
    # | "WHILE" comparison "REPEAT" nl {statement} "ENDWHILE" nl
    # | "LABEL" ident nl
    # | "GOTO" ident nl
    # | "LET" ident "=" expression nl
    # | "INPUT" ident nl
    def statement(self):

        if(self.check_token(TokenType.PRINT)):

            self.next_token()

            if(self.check_token(TokenType.STRING)):
                self.emitter.emit_line("printf(\"" + self.curr_token.text + "\\n\");")
                self.next_token()
            else:
                self.emitter.emit("printf(\"%" + ".2f\\n\", (float)(")
                self.expression()
                self.emitter.emit_line("));")

        elif(self.check_token(TokenType.IF)):

            self.next_token()
            self.emitter.emit("if(")
            self.comparison()

            self.match(TokenType.THEN)
            self.nl()
            self.emitter.emit_line("){")

            while not (self.check_token(TokenType.ENDIF)):
                self.statement()

            self.match(TokenType.ENDIF)
            self.emitter.emit_line("}")
        
        elif(self.check_token(TokenType.WHILE)):

            self.next_token()
            self.emitter.emit("while(")
            self.comparison()

            self.match(TokenType.REPEAT)
            self.nl()
            self.emitter.emit_line("){")

            while not(self.check_token(TokenType.ENDWHILE)):
                self.statement()

            self.match(TokenType.ENDWHILE)
            self.emitter.emit_line("}")
        
        elif(self.check_token(TokenType.LABEL)):

            self.next_token()
            
            if self.curr_token.text in self.labels_declared:
                self.abort("Label already exists: " + self.curr_token.text)
            self.labels_declared.add(self.curr_token.text)

            self.emitter.emit_line(self.curr_token.text + ":")
            self.match(TokenType.IDENT)
        
        elif(self.check_token(TokenType.GOTO)):

            self.next_token()
            self.labels_gotoed.add(self.curr_token.text)
            self.emitter.emit_line("goto" + self.curr_token.text + ";")
            self.match(TokenType.IDENT)
        
        elif self.check_token(TokenType.LET):

            self.next_token()

            if self.curr_token.text not in self.symbols:
                self.symbols.add(self.curr_token.text)
                self.emitter.header_line("float " + self.curr_token.text + ";")

            self.emitter.emit(self.curr_token.text + " = ")
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)

            self.expression()
            self.emitter.emit_line(";")

        elif self.check_token(TokenType.INPUT):
            self.next_token()

            if self.curr_token.text not in self.symbols:
                self.symbols.add(self.curr_token.text)
                self.emitter.header_line("float " + self.curr_token.text + ";")

            self.emitter.emit_line("if(0 == scanf(\"%" + "f\", &" + self.curr_token.text + ")) {")
            self.emitter.emit_line(self.curr_token.text + " = 0;")
            self.emitter.emit("scanf(\"%")
            self.emitter.emit_line("*s\");")
            self.emitter.emit_line("}")
            self.match(TokenType.IDENT)
        
        else:
            self.abort("Invalid statement at " + self.curr_token.text + " (" + self.curr_token.kind.name + ")") 

        self.nl()
    
    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self):

        self.expression()

        if self.is_comparison_operator():
            self.emitter.emit(self.curr_token.text)
            self.next_token()
            self.expression()
        else:
            self.abort("Expected comparison operator at: " + self.curToken.text)
        
        while self.is_comparison_operator():
            self.emitter.emit(self.curr_token.text)
            self.next_token()
            self.expression()
    
    # expression ::= term {( "-" | "+" ) term}
    def expression(self):

        self.term()
        while self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.emitter.emit(self.curr_token.text)
            self.next_token()
            self.term()
    
    # term ::= unary {( "/" | "*" ) unary}
    def term(self):

        self.unary()

        while self.check_token(TokenType.ASTERISK) or self.check_token(TokenType.SLASH):
            self.emitter.emit(self.curr_token.text)
            self.next_token()
            self.unary()
    
    # unary ::= ["+" | "-"] primary
    def unary(self):

        if self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.emitter.emit(self.curr_token.text)
            self.next_token()
        self.primary()

    def primary(self):
        
        if self.check_token(TokenType.NUMBER):
            self.emitter.emit(self.curr_token.text)
            self.next_token()
        elif self.check_token(TokenType.IDENT):
            if self.curr_token.text not in self.symbols:
                self.abort("Referencing variable before assignment: " + self.curr_token.text)

            self.emitter.emit(self.curr_token.text)    
            self.next_token()
        else:
            self.abort("Unexpected token at " + self.curr_token.text)
        
    
    def nl(self):

        self.match(TokenType.NEWLINE)

        while(self.check_token(TokenType.NEWLINE)):
            self.next_token()
    
    
