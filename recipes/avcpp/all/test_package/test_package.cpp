#include "avcpp/av.h"
#include "avcpp/avutils.h"

int main() {
    av::init();
    av::setFFmpegLoggingLevel(AV_LOG_DEBUG);

    return 0;
}
