#include <cstdlib>
#include <iostream>
#include <wx/utils.h>
#include <wx/init.h>

int main() {
    wxVersionInfo vi = wxGetLibraryVersionInfo();
    std::cout << "wxWidgets version: ";
    std::cout << vi.GetMajor() << ".";
    std::cout << vi.GetMinor() << ".";
    std::cout << vi.GetMicro() << std::endl;
    return EXIT_SUCCESS;
}
