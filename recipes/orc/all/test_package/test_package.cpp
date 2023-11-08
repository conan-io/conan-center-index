#include <orc/OrcFile.hh>
#include <orc/Reader.hh>
#include <cstdlib>
#include <iostream>
#include <memory>

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <orc-file-path>" << std::endl;
        return -1;
    }

    try {
        std::unique_ptr<orc::InputStream> input = orc::readLocalFile(argv[1]);
        orc::ReaderOptions options;
        std::unique_ptr<orc::Reader> reader = orc::createReader(std::move(input), options);

        std::cout << "Number of rows: " << reader->getNumberOfRows() << std::endl;
        std::cout << "Number of columns: " << reader->getType().getSubtypeCount() << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
