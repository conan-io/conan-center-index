#include <iostream>

#include <mysqlx/xdevapi.h>


int main() {
    mysqlx::Value col1("version");
    mysqlx::Value col2("8.0.25");

    mysqlx::Row simulatedRow;
    simulatedRow.set(0, col1);
    simulatedRow.set(1, col2);

    std::string variable_name = simulatedRow[0].get<std::string>();
    std::string version_value = simulatedRow[1].get<std::string>();

    int major_version;
    std::stringstream version_stream(version_value);
    version_stream >> major_version;

    std::cout << "Variable name: " << variable_name << std::endl;
    std::cout << "Major version: " << major_version << std::endl;

    return EXIT_SUCCESS;
}
