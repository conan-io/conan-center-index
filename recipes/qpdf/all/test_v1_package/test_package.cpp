#include <qpdf/DLL.h>
#include <qpdf/QPDF.hh>
#include <qpdf/QPDFWriter.hh>
#include <iostream>

int main(int argc, char* argv[])
{
    std::cout << "QPDF_VERSION " << QPDF_VERSION << "\n";

    if (argc != 2) {
        std::cerr << "need one parameter as output pdf path.";
        return 1;
    }
    char const* filename = argv[1];

    try {
        QPDF pdf;
        pdf.emptyPDF();
        QPDFWriter w(pdf, filename);
        w.write();
    } catch (std::exception& e) {
        std::cerr << e.what() << std::endl;
        exit(2);
    }

    return 0;
}
