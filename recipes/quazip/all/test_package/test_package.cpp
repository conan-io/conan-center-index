#include <iostream>
#include <quazip/quazip.h>

int main(int argc, char* argv[]) {


    std::cout << "Quazip test_package" << std::endl;

    const QString path = QString::fromLatin1(argv[1]);

    QuaZip zip(path);

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
