#include <opencv2/face/facerec.hpp>

int main() {
    auto face_recognizer = cv::face::FisherFaceRecognizer::create();
    return 0;
}
