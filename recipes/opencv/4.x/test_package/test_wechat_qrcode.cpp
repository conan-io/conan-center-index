#include <opencv2/core.hpp>
#include <opencv2/wechat_qrcode.hpp>

int main() {
    cv::Mat image = cv::Mat::ones(100, 100, CV_8UC3) * 50;
    cv::wechat_qrcode::WeChatQRCode wechat_qrcode;
    auto decoded_strings = wechat_qrcode.detectAndDecode(image);
    return 0;
}
