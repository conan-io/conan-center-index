#include <stdio.h>

#include "qcbor/qcbor_encode.h"
#include "qcbor/qcbor_decode.h"
#include "qcbor/qcbor_spiffy_decode.h"

int main() {
  UsefulBuf_MAKE_STACK_UB(EngineBuffer, 300);
  UsefulBufC EncodedEngine;

  QCBOREncodeContext EncodeCtx;
  QCBOREncode_Init(&EncodeCtx, EngineBuffer);

  QCBOREncode_CloseArray(&EncodeCtx);
  QCBOREncode_CloseMap(&EncodeCtx);

  return 0;
}
