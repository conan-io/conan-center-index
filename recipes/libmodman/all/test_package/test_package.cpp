#include "libmodman/module_manager.hpp"

#include "test_module.hpp"

#include <cstdint>
#include <iostream>
#include <cstring>

int main(int argc, char *argv[])
{
    libmodman::module_manager mm;

    if (!mm.register_type<my_extension>()) {
        std::cerr << "Unable to register type!\n";
        return 1;
    }

    if (!mm.load_dir(argv[1]) && argc > 2) {
        if (!mm.load_dir(argv[1], false)) {
            std::cerr << "Unable to load modules!\n";
            return 1;
        }
    }

    std::vector<my_extension *> exts = mm.get_extensions<my_extension>();

    std::cout << "Found " << exts.size() << " extensions:\n";
    for (unsigned int j = 0; j < exts.size(); j++) {
        std::cout << "- " << typeid(*(exts[j])).name() << "\n";
        for (int i = 0; i < 20; ++i) {
            std::cout << "  f(" << i << ") = " << exts[j]->expensive_operation(i) << "\n";
        }
    }
    if (exts.size() != 2) {
        std::cerr << "Wrong number of extensions found!\n";
        return 1;
    }
    return 0;
}
