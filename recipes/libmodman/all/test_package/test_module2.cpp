#include "test_module.hpp"

class mod2 : public my_extension {
    int expensive_operation(const int nb) const override {
        return nb * nb;
    }
};

MM_MODULE_INIT_EZ(mod2, true, NULL, NULL);
