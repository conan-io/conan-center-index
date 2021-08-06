#include <stdio.h>
#include "com/amazonaws/kinesis/video/client/Include.h"

int main(int argc, char *argv[])
{
    PDeviceInfo myDeviceInfo;
    PClientCallbacks myPClientCallbacks;
    PCLIENT_HANDLE myHandle;
    createKinesisVideoClient(myDeviceInfo, myPClientCallbacks, myHandle);

    printf("aws-kps-pic test_package ran successfully \n");

    return 0;
}
