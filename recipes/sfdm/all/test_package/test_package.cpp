#include <sfdm/sfdm.hpp>


int main(void) {
    sfdm::DecodeResult{};
#ifdef SFDM_WITH_ZXING_DECODER
    sfdm::ZXingCodeReader{};
#endif
#ifdef SFDM_WITH_LIBDMTX_DECODER
    sfdm::LibdmtxCodeReader{};
#endif
#if defined(SFDM_WITH_ZXING_DECODER) && defined(SFDM_WITH_LIBDMTX_DECODER)
    sfdm::LibdmtxZXingCombinedCodeReader{};
#endif

    return 0;
}
