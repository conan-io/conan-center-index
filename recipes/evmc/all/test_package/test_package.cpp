#include <iostream>
#include <cstdlib>

#include <evmc/evmc.h>
#include <evmc/evmc.hpp>
#include <evmc/filter_iterator.hpp>
#include <evmc/helpers.h>
#include <evmc/hex.hpp>
#include <evmc/instructions.h>
#include <evmc/loader.h>
#include <evmc/mocked_host.hpp>
#include <evmc/utils.h>

int main() {
    const auto table = evmc_get_instruction_names_table(EVMC_BYZANTIUM);
    std::cout << "HEX 0x80: " << evmc::hex(0x80) << std::endl;

    return EXIT_SUCCESS;
}
