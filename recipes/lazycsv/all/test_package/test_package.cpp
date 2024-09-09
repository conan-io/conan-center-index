#include <iostream>
#include "lazycsv.hpp"


int main(void) {
    std::string csv_data{ "name,lastname,age\nPeter,Griffin,45\nchris,Griffin,14\n" };

    lazycsv::parser<std::string_view> parser_a{ csv_data };
    lazycsv::parser<std::string> parser_b{ csv_data };
}
