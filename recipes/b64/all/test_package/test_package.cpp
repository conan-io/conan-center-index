#include <iostream>

extern "C" {
    #include "b64/cencode.h"
    #include "b64/cdecode.h"
}

int main() {
    const char str[] = "Hello world!";
    const unsigned len = sizeof(str);
    char out[len*2] = {0}, rev[len*2] = {0};
    
    base64_encodestate E;
    base64_init_encodestate(&E);
    base64_decodestate D;
    base64_init_decodestate(&D);
    
    const unsigned out_len = base64_encode_block(str, len, out, &E);
    base64_decode_block(out, out_len, rev, &D);

    std::cout << "input:    " << str << std::endl;
    std::cout << "base64:   " << out << std::endl;
    std::cout << "reversed: " << rev << std::endl;

    return 0;
}
