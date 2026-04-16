#include <stdio.h>
#include "msquic.h"

int main(void) {
    const QUIC_API_TABLE *MsQuic = NULL;
    QUIC_STATUS Status = MsQuicOpen2(&MsQuic);

    if (QUIC_SUCCEEDED(Status)) {
        printf("MsQuic loaded successfully\n");
        MsQuicClose(MsQuic);
    } else {
        printf("MsQuic load failed: 0x%x\n", Status);
    }

    return 0;
}
