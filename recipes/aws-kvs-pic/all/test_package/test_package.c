#include <stdio.h>
#include "com/amazonaws/kinesis/video/client/Include.h"

int main(int argc, char *argv[])
{

    CLIENT_HANDLE clientHandle = INVALID_CLIENT_HANDLE_VALUE;
    PDeviceInfo pDeviceInfo = NULL;
    PClientCallbacks pClientCallbacks = NULL;

    createKinesisVideoClient(pDeviceInfo, pClientCallbacks, &clientHandle);

    printf("aws-kps-pic test_package ran successfully \n");

    return 0;
}
