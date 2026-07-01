#include <iostream>
#include <cstdint>
#include "cineformsdk/CFHDDecoder.h"
#include "cineformsdk/CFHDEncoder.h"

int main(void) {
    CFHD_Error error = CFHD_ERROR_OKAY;
    CFHD_DecoderRef mDecoderRef = nullptr;

    error = CFHD_OpenDecoder(&mDecoderRef, nullptr);    

    if(error != CFHD_ERROR_OKAY){
        std::cout << "Failed to CFHD_OpenDecoder" << std::endl;
        return 1;
    }

    error = CFHD_CloseDecoder(mDecoderRef);    
    if(error != CFHD_ERROR_OKAY){
        std::cout << "Failed to CFHD_CloseDecoder" << std::endl;
        return 1;
    }
    return 0;
}
