#include <iostream>

#include <wx/pdfdoc.h>
#include <wx/pdfdoc_version.h>

int main()
{
    std::cout << PDFDOC_VERSION_STRING << std::endl;

    wxPdfDocument pdf;

    return 0;
}