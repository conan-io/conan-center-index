#include "mc_parser.hpp"

static const int VARS[] = {
    NUM,
    OPA,
    NUM,
    STOP,
    0,
};

int yylex() {
    static unsigned pos = 0;
    if (pos > (sizeof(VARS) / sizeof(*VARS))) {
        return 0;
    }
    int r = VARS[pos];
    ++pos;
    return r;
}
