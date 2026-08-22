#include <iostream>
#include "PDFWriter/PDFWriter.h"

int main(void) {
    PDFWriter pdfWriter;

    auto status = pdfWriter.StartPDF(
        "test_package.pdf",
        ePDFVersion13,
        LogConfiguration(true, true, "AppendPagesTestLog.txt")
    );

    if (status != PDFHummus::eSuccess) {
        std::cerr << "failed to create pdf" << std::endl;
        return 1;
    }

    status = pdfWriter.EndPDF();

    if (status != PDFHummus::eSuccess) {
        std::cerr << "failed to close pdf" << std::endl;
        return 1;
    }

    return 0;
}
