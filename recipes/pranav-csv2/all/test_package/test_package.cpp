#include "csv2/reader.hpp"

int main() {
    csv2::Reader<
        csv2::delimiter<','>,
        csv2::quote_character<'"'>, 
        csv2::first_row_is_header<true>,
        csv2::trim_policy::trim_whitespace> csv;

    csv.rows();

    return 0;
}
