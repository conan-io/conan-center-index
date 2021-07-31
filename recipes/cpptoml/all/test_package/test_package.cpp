#include <cstdlib>
#include <iostream>
#include <cpptoml.h>

int main()
{
    std::cout << "Bincrafters\n";
    
    
    std::shared_ptr<cpptoml::table> root = cpptoml::make_table();
    root->insert("Integer", 1234L);
    root->insert("Double", 1.234);
    root->insert("String", std::string("ABCD"));

    auto table = cpptoml::make_table();
    table->insert("ElementOne", 1L);
    table->insert("ElementTwo", 2.0);
    table->insert("ElementThree", std::string("THREE"));

    auto nested_table = cpptoml::make_table();
    nested_table->insert("ElementOne", 2L);
    nested_table->insert("ElementTwo", 3.0);
    nested_table->insert("ElementThree", std::string("FOUR"));

    table->insert("Nested", nested_table);

    root->insert("Table", table);

    auto int_array = cpptoml::make_array();
    int_array->push_back(1L);
    int_array->push_back(2L);
    int_array->push_back(3L);
    int_array->push_back(4L);
    int_array->push_back(5L);

    root->insert("IntegerArray", int_array);

    auto double_array = cpptoml::make_array();
    double_array->push_back(1.1);
    double_array->push_back(2.2);
    double_array->push_back(3.3);
    double_array->push_back(4.4);
    double_array->push_back(5.5);

    root->insert("DoubleArray", double_array);

    auto string_array = cpptoml::make_array();
    string_array->push_back(std::string("A"));
    string_array->push_back(std::string("B"));
    string_array->push_back(std::string("C"));
    string_array->push_back(std::string("D"));
    string_array->push_back(std::string("E"));

    root->insert("StringArray", string_array);

    auto table_array = cpptoml::make_table_array();
    table_array->push_back(table);
    table_array->push_back(table);
    table_array->push_back(table);

    root->insert("TableArray", table_array);

    auto array_of_arrays = cpptoml::make_array();
    array_of_arrays->push_back(int_array);
    array_of_arrays->push_back(double_array);
    array_of_arrays->push_back(string_array);

    root->insert("ArrayOfArrays", array_of_arrays);

    std::cout << (*root);
    return 0;
}
