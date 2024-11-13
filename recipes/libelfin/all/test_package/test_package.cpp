#include <libelfin/elf/data.hh>
#include <iostream>

int main() {
    elf::pt pt_obj = elf::pt::load;
    std::cout << elf::to_string(pt_obj) << std::endl;
    return 0;
}
