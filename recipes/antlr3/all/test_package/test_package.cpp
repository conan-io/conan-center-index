#include "ExprLexer.hpp"
#include "ExprParser.hpp"

#include <cstdlib>
#include <iostream>
#include <string>

int main() {
    using namespace test_expr;
    std::string input = "40 + 5 - 3";
    ANTLR_UINT8 name[] = "test";
    ExprLexerTraits::InputStreamType in(reinterpret_cast<const ANTLR_UINT8*>(input.data()),
                                        ANTLR_ENC_UTF8, input.size(),
                                        name);
    ExprLexer lexer(&in);
    ExprParserTraits::TokenStreamType tokens(ANTLR_SIZE_HINT, lexer.get_tokSource());
    ExprParser parser(&tokens);
    long v = parser.expr();
    std::cout << input << " = " << v << std::endl;
    return v == 42 ? EXIT_SUCCESS : EXIT_FAILURE;
}
