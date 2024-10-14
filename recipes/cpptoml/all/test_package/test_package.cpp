#include <cpptoml.h>

#include <cstdlib>
#include <iostream>

int main()
{
    std::shared_ptr<cpptoml::table> root = cpptoml::make_table();
    root->insert("Integer", 1234L);
    root->insert("Double", 1.234);
    root->insert("String", std::string("ABCD"));
}
