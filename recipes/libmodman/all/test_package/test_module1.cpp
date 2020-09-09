#include "test_module.hpp"

class mod1 : public my_extension {
    int expensive_operation(const int nb) const override {
        if (nb < 0) {
            return 0;
        }
        if (nb == 0) {
            return 1;
        }
        int a = 0, b = 1;
        for (int i = 0; i < nb; ++i) {
            int n = a + b;
            a = b;
            b = n;
        }
        return b;
    }
};

MM_MODULE_INIT_EZ(mod1, true, NULL, NULL);
