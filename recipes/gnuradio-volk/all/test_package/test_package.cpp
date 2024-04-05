#include <volk/volk.h>

int main() {
    int N = 10;
    unsigned int alignment = volk_get_alignment();
    float* in = (float*)volk_malloc(sizeof(float)*N, alignment);
    float* out = (float*)volk_malloc(sizeof(float)*N, alignment);

    in[0] = 0.000;
    in[1] = 0.524;
    in[2] = 0.786;
    in[3] = 1.047;
    in[4] = 1.571;
    in[5] = 1.571;
    in[6] = 2.094;
    in[7] = 2.356;
    in[8] = 2.618;
    in[9] = 3.142;

    volk_32f_cos_32f(out, in, N);

    for(unsigned int ii = 0; ii < N; ++ii){
        printf("cos(%1.3f) = %1.3f\n", in[ii], out[ii]);
    }

    volk_free(in);
    volk_free(out);
}
