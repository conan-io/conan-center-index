grammar Expr;

options {
    language = Cpp;
}

@lexer::traits {
    class ExprLexer;
    class ExprParser;
    typedef antlr3::Traits<ExprLexer, ExprParser> ExprLexerTraits;
    typedef ExprLexerTraits ExprParserTraits;
}

@parser::includes {
#include "ExprLexer.hpp"
}

@lexer::namespace { test_expr }
@parser::namespace { test_expr }

expr returns [long v]
    : a=term { $v = $a.v; } ( '+' b=term { $v += $b.v; } | '-' b=term { $v -= $b.v; } )* EOF
    ;

term returns [long v]
    : INT { $v = std::stol($INT.text); }
    ;

INT : ('0'..'9')+ ;
WS  : (' ' | '\t' | '\n' | '\r')+ { $channel = HIDDEN; } ;
