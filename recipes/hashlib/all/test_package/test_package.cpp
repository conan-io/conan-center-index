#include <iostream>
#include <string>
#include <hashlib/md5.hpp>

int main() {
    std::string input = "hello world";
    hashlib::md5 md5;
    md5.update(input);
    std::cout << md5.hexdigest() << std::endl;
}