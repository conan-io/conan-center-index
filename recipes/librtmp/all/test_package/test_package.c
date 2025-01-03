#include <librtmp/rtmp.h>

int main() {
    RTMP rtmp = { 0 };
    RTMP_Init(&rtmp);
    RTMP_Close(&rtmp);
    return 0;
}
