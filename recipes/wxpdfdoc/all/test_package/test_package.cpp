#include <iostream>

// For compilers that support precompilation, includes "wx/wx.h".
#include "wx/wxprec.h"

#ifdef __BORLANDC__
#pragma hdrstop
#endif

#ifndef WX_PRECOMP
#include "wx/wx.h"
#endif

#include <wx/pdfdoc.h>
#include <wx/pdfdoc_version.h>

int main()
{
    std::cout << PDFDOC_VERSION_STRING << std::endl;

    wxPdfDocument pdf;

    return 0;
}