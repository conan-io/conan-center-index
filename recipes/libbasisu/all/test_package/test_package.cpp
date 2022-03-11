#include <libbasisu/transcoder/basisu_transcoder.h>
#include <iostream>

int main() {
    basist::basisu_transcoder_init();
    std::cout << "Basisu successfuly initialized, format localized: "
        << basist::basis_get_format_name(basist::transcoder_texture_format::cTFETC2_RGBA)
        << std::endl;
    return 0;
}
