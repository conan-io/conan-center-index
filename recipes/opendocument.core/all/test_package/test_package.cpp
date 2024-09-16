#include <odr/document.hpp>
#include <odr/document_element.hpp>
#include <odr/html.hpp>
#include <odr/exceptions.hpp>

int main() {
    try {
        odr::DocumentFile document_file{"test_package.xlsx"};
        auto document = document_file.document();
        auto element = document.root_element();
        auto text = element.text();
        text.set_content("hello world!");
    }
    catch (const odr::FileNotFound& ex) {
    }

    return 0;
}
