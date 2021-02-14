#include <iostream>
#include <quazip/quazip.h>

int main(int argc, char* argv[]) {


    std::cout << "Quazip test_package" << std::endl;

    QuaZip zip(argv[1]);

    if (zip.open(QuaZip::mdUnzip)) {

        std::cout << "zipFile opened. It contains the following files:" << std::endl;

        for (bool more = zip.goToFirstFile(); more; more = zip.goToNextFile()) {
            std::cout << zip.getCurrentFileName().toUtf8().constData() << std::endl;
        }

        if (zip.getZipError() == UNZ_OK) {
            // ok, there was no error
        }

    } else {
        std::cout << "Error opening zipFile" << std::endl;
    }

    return 0;
}
