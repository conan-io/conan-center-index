#include "bacnet/apdu.h"
#include "bacnet/bacdef.h"
#include "bacnet/bactext.h"
#include "bacnet/basic/binding/address.h"
#include "bacnet/basic/object/device.h"
#include "bacnet/basic/services.h"
#include "bacnet/basic/sys/filename.h"
#include "bacnet/basic/tsm/tsm.h"
#include "bacnet/config.h"
#include "bacnet/datalink/datalink.h"
#include "bacnet/datalink/dlenv.h"
#include "bacnet/iam.h"
#include "bacnet/npdu.h"
#include "bacnet/version.h"
#include <errno.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

static void MyAbortHandler(BACNET_ADDRESS *src, uint8_t invoke_id,
                           uint8_t abort_reason, bool server) {
  (void)src;
  (void)invoke_id;
  (void)server;
  printf("BACnet Abort: %s\n", bactext_abort_reason_name(abort_reason));
}

static void MyRejectHandler(BACNET_ADDRESS *src, uint8_t invoke_id,
                            uint8_t reject_reason) {
  (void)src;
  (void)invoke_id;
  printf("BACnet Reject: %s\n", bactext_reject_reason_name(reject_reason));
}

static void Init_Service_Handlers(void) {
  Device_Init(NULL);
  apdu_set_unconfirmed_handler(SERVICE_UNCONFIRMED_WHO_IS, handler_who_is);
  apdu_set_unrecognized_service_handler_handler(handler_unrecognized_service);
  apdu_set_confirmed_handler(SERVICE_CONFIRMED_READ_PROPERTY,
                             handler_read_property);
  apdu_set_unconfirmed_handler(SERVICE_UNCONFIRMED_I_AM, handler_i_am_add);
  apdu_set_abort_handler(MyAbortHandler);
  apdu_set_reject_handler(MyRejectHandler);
}

int main(int argc, char *argv[]) {

  address_init();
  Device_Set_Object_Instance_Number(BACNET_MAX_INSTANCE);
  Init_Service_Handlers();
  address_init();
  dlenv_init();

  return 0;
}
