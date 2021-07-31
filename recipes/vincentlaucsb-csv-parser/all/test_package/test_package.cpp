#include "csv.hpp"

#include <sstream>
#include <iostream>

int main() {
    using namespace csv;
    std::stringstream rows("A,B,C\n"
                           "1,2,3\n"
                           "4,5,6");

    CSVReader reader(rows);

    std::vector<std::string> col_names = reader.get_col_names();
    for (auto name : col_names)
        std::cout << name << ", ";

    CSVRow row;
    if (reader.read_row(row)){
        for (auto& field : row)
            std::cout << std::string(field) << ", ";
    }

    return 0;
}
