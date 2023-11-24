#include <cstdlib>
#include <iostream>
#include <wx/utils.h>
#include <wx/init.h>
#if wxUSE_STC
#include <wx/stc/stc.h>
#endif

int main()
{
    int argc = 0;
    wxChar * argv[] = {NULL};
    if (!wxEntryStart(argc, argv)) {
        std::cerr << "wxEntryStart failed!" << std::endl;
        return EXIT_FAILURE;
    }
    wxVersionInfo vi = wxGetLibraryVersionInfo();
    std::cout << "wxWidgets version: ";
    std::cout << vi.GetMajor() << ".";
    std::cout << vi.GetMinor() << ".";
    std::cout << vi.GetMicro() << std::endl;
#if wxUSE_STC
    wxStyledTextCtrl * stc = new wxStyledTextCtrl();
#endif
    wxEntryCleanup();
    return EXIT_SUCCESS;
}
