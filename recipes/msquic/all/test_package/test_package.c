#include <stdio.h>
#include "msquic.h"
int main(void) {
    const QUIC_API_TABLE *MsQuic = NULL;
    QUIC_STATUS Status = MsQuicOpen2(&MsQuic);
    if (QUIC_FAILED(Status)) {
        printf("MsQuicOpen2 failed: 0x%x\n", (unsigned)Status);
        return 1;
    }
    MsQuicClose(MsQuic);
    return 0;
}
