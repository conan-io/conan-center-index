#include "opencv2/objdetect/objdetect.hpp"
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"

#include <iostream>
#include <cstdlib>

using namespace cv;

/** Global variables */
String face_cascade_name = "haarcascades/haarcascade_frontalface_alt.xml";
String eyes_cascade_name = "haarcascades/haarcascade_eye_tree_eyeglasses.xml";
CascadeClassifier face_cascade;
CascadeClassifier eyes_cascade;
std::string window_name = "Capture - Face detection";
RNG rng(12345);

void faceDetection( Mat frame ) {
    std::vector<Rect> faces;
    Mat frame_gray;

    cvtColor(frame, frame_gray, COLOR_BGR2GRAY);
    equalizeHist( frame_gray, frame_gray );

    face_cascade.detectMultiScale(frame_gray, faces, 1.1, 2, 0 | CASCADE_SCALE_IMAGE, Size(30, 30));

    for (size_t i = 0; i < faces.size(); i++) {
        Point center( faces[i].x + faces[i].width*0.5, faces[i].y + faces[i].height*0.5 );
        ellipse( frame, center, Size( faces[i].width*0.5, faces[i].height*0.5), 0, 0, 360, Scalar( 255, 0, 255 ), 4, 8, 0 );

        Mat faceROI = frame_gray( faces[i] );
        std::vector<Rect> eyes;

        eyes_cascade.detectMultiScale(faceROI, eyes, 1.1, 2, 0 | CASCADE_SCALE_IMAGE, Size(30, 30));

        for (size_t j = 0; j < eyes.size(); j++) {
            Point center( faces[i].x + eyes[j].x + eyes[j].width*0.5, faces[i].y + eyes[j].y + eyes[j].height*0.5 );
            int radius = cvRound( (eyes[j].width + eyes[j].height)*0.25 );
            circle( frame, center, radius, Scalar( 255, 0, 0 ), 4, 8, 0 );
        }
    }
}


int main( int argc, const char** argv ) {
    CvCapture* capture;

    const String res_folder = String(argv[1]) + "/";
    const String face_cascade_path = res_folder + "/" + face_cascade_name;
    const String eyes_cascade_path = res_folder + "/" + eyes_cascade_name;

    if (!face_cascade.load(face_cascade_path)) {
        std::cerr << "--(!)Error loading" << std::endl;
        return EXIT_FAILURE;
    }
    if (!eyes_cascade.load(eyes_cascade_path)) {
        std::cerr << "--(!)Error loading" << std::endl;
        return EXIT_FAILURE;
    }

    Mat frame = imread(argv[2]);
    if (!frame.empty()) {
        faceDetection(frame);
    }

    return EXIT_SUCCESS;
}
