#include <wx/wxsqlite3.h>
#include <iostream>

int main()
{
    std::cout << "wxSQLite3 Version: " << wxSQLite3Database::GetWrapperVersion().mb_str(wxConvUTF8)
              << std::endl;

    return 0;
}