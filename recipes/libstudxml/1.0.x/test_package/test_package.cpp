#include <xml/parser>
#include <sstream>

int main() {
    std::istringstream is("<root><nested>X</nasted></root>");
    xml::parser p(is, "test");

    bool success = true;
    success &= p.next() == xml::parser::start_element;
    success &= p.next() == xml::parser::start_element;
    success &= p.next() == xml::parser::characters && p.value() == "X";

    return success ? 0 : -1;
}
