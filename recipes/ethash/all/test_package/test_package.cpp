#include <ethash/ethash.hpp>

int main(int argc, char **) {
    auto epoch_num = ethash::get_epoch_number(0);
    return 0;
}
