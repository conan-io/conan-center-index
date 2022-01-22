#include <kiss_fft.h>

#include <cstdlib>
#include <iostream>

int main()
{
    std::cout << "kiss_fft_next_fast_size(1) = " << kiss_fft_next_fast_size(1) << std::endl;
    return EXIT_SUCCESS;
}
