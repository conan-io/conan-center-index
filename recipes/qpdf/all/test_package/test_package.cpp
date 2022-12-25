#include <qpdf/DLL.h>
#include <qpdf/QPDF.hh>
#include <qpdf/QPDFWriter.hh>
#include <iostream>

int main(int argc, char* argv[])
{
    std::cout << "QPDF_VERSION " << QPDF_VERSION << "\n";

    try {
        QPDF pdf;
        pdf.emptyPDF();
        QPDFWriter w(pdf, "empty_example.pdf");
        w.write();
    } catch (std::exception& e) {
        std::cerr << e.what() << "\n";
        exit(2);
    }

    return 0;
}
