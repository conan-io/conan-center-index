#include <iostream>
#include <sstream>
#include <DecimalNative.hpp>

using namespace epam::deltix::dfp;

int main(int argc, char *argv[]) {
    if(argc!=4) {
        std::cout << "Usage: <A> <op> <B>" << std::endl;
		return 0;
	}

    const Decimal64 x(argv[1]); // Parsing call example - can throw std::invalid_argument

    const char* op = argv[2];

    std::stringstream arg3(argv[3]); // Input from stream
    Decimal64 y;
    arg3 >> y;

    Decimal64 z;
    switch (*op) {
    case '+':
        z = x + y;
        break;
    case '-':
        z = x - y;
        break;
    case '*':
        z = x * y;
        break;
    case '/':
        z = x / y;
        break;
    default:
        std::cerr << "Unsupported operation '" << op << "'" << std::endl;
        return 1;
    }

    std::cout << x << "(=" << x.toUnderlying() << ") " << op << " " << (std::string)y << "(=" << y.toUnderlying() << ") = " << z << "(=" << z.toUnderlying() << ")" << std::endl;
	return 0;
}
