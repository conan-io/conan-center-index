#include <kiss_fft.h>

#include <stdio.h>

int main()
{
    printf("kiss_fft_next_fast_size(1) = %i\n", kiss_fft_next_fast_size(1));
    return 0;
}
