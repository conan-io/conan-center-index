#include <ultrahdr_api.h>
#include <iostream>

int main()
{
    uhdr_codec_private_t* decoder = uhdr_create_decoder();
    std::cout << "Creating new decoder " << decoder << "\n";
    std::cout << "Releasing decoder " << "\n";
    uhdr_release_decoder(decoder);

    return 0;
}
