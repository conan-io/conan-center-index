#include "poppler-document.h"

#include <cstdlib>
#include <iostream>

using namespace poppler;

int main(int argc, char **argv) {
    if (argc < 2) {
        std::cerr << "Need an argument\n";
        return EXIT_FAILURE;
    }

    auto doc = document::load_from_file(argv[1]);
    std::cout << "#pages: " << doc->pages() << '\n';
    std::cout << "title: " << doc->get_title().to_latin1() << '\n';
    std::cout << "author: " << doc->get_author().to_latin1() << '\n';
    std::cout << "subject: " << doc->get_subject().to_latin1() << '\n';
    std::cout << "keywords: " << doc->get_keywords().to_latin1() << '\n';

    return EXIT_SUCCESS;
}
