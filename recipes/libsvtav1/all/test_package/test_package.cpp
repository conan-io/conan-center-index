#include "EbSvtAv1Enc.h"
#ifdef HAVE_DECODER
#   include "EbSvtAv1Dec.h"
#endif

#include <iostream>

int main() { std::cout << svt_av1_get_version() << "\n"; }
