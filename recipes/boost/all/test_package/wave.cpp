#include <iostream>
#include <string>
#include <boost/wave.hpp>
#include <boost/wave/cpplexer/cpp_lex_token.hpp>
#include <boost/wave/cpplexer/cpp_lex_iterator.hpp>

int main() {
    std::string input = "#define HELLO 42\nHELLO\n";

    typedef boost::wave::cpplexer::lex_token<> token_type;
    typedef boost::wave::cpplexer::lex_iterator<token_type> lex_iterator_type;
    typedef boost::wave::context<std::string::iterator, lex_iterator_type> context_type;

    context_type ctx(input.begin(), input.end(), "test.cpp");

    std::cout << "Testing Boost::Wave: ";
    for (auto const& tok : ctx)
        std::cout << tok.get_value();

    std::cout << std::endl;
    return 0;
}