// For compilers that support precompilation, includes "wx/wx.h".
#include <wx/wxprec.h>

#ifdef __BORLANDC__
#pragma hdrstop
#endif

#ifndef WX_PRECOMP
#include <wx/wx.h>
#endif

#include <wx/wxsqlite3.h>

#include <iostream>

int main()
{
    std::cout << "wxSQLite3 Version: "
              << (const char*) wxSQLite3Database::GetWrapperVersion().mb_str(wxConvUTF8)
              << std::endl;

    std::cout << "Initialize SQLite" << std::endl;
    wxSQLite3Database::InitializeSQLite();

    wxSQLite3Database db;

    std::cout << "Shutdown SQLite" << std::endl;
    wxSQLite3Database::ShutdownSQLite();

    return 0;
}