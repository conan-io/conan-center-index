#include <opencv2/videoio.hpp>
#include <opencv2/videoio/registry.hpp>

#include <stdexcept>

int main() {
    if (!cv::videoio_registry::hasBackend(cv::CAP_FFMPEG))
        throw std::runtime_error("FFmpeg backend was not found");

    return 0;
}
