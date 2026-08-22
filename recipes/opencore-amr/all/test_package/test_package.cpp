#include <opencore-amrnb/interf_dec.h>
#include <opencore-amrwb/dec_if.h>

int main(int, char**)
{
    // create AMR-NB decode context and destroy it
    void* nb_decoder = Decoder_Interface_init();
    Decoder_Interface_exit(nb_decoder);

    // create AMR-WB decode context and destroy it
    void* wb_decoder = D_IF_init();
    D_IF_exit(wb_decoder);

    return 0;
}
