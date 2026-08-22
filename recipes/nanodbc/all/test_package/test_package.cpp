#include <nanodbc/nanodbc.h>

#include <iostream>
using namespace nanodbc;

int main(int /*argc*/, char* /*argv*/[])
{
    try
    {
        auto const connection_string = NANODBC_TEXT("");
        connection conn(connection_string);
        conn.dbms_name();
    }
    catch (std::runtime_error const& e)
    {
        std::cerr << e.what() << std::endl;
    }
}
