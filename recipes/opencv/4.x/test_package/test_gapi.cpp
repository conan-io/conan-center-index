#include <opencv2/gapi.hpp>
#include <opencv2/gapi/core.hpp>
#include <opencv2/gapi/imgproc.hpp>

int main() {
    // derived from https://docs.opencv.org/4.5.0/d0/d1e/gapi.html
    cv::GMat in;
    cv::GMat vga = cv::gapi::resize(in, cv::Size(), 0.5, 0.5);
    cv::GMat gray = cv::gapi::BGR2Gray(vga);
    cv::GMat blurred = cv::gapi::blur(gray, cv::Size(5,5));
    cv::GMat edges = cv::gapi::Canny(blurred, 32, 128, 3);
    cv::GMat b,g,r;
    std::tie(b,g,r) = cv::gapi::split3(vga);
    cv::GMat out = cv::gapi::merge3(b, g | edges, r);
    cv::GComputation ac(in, out);

    return 0;
}
