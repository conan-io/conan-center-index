#include <correct.h>

int main(void) {
    correct_convolutional *conv;

    conv = correct_convolutional_create(2, 6, correct_conv_r12_6_polynomial);
    correct_convolutional_destroy(conv);

    return 0;
}
