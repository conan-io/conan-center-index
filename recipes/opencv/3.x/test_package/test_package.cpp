#include "opencv2/objdetect/objdetect.hpp"
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"

#include <iostream>
#include <cstdlib>

using namespace cv;


int main( int argc, const char** argv ) {
    String face_cascade_name = "haarcascades/haarcascade_frontalface_alt.xml";
    String eyes_cascade_name = "haarcascades/haarcascade_eye_tree_eyeglasses.xml";
    CascadeClassifier face_cascade;
    CascadeClassifier eyes_cascade;

    const String res_folder = String(argv[1]) + "/";
    face_cascade_name.insert(0, res_folder);
    eyes_cascade_name.insert(0, res_folder);

    if (!face_cascade.load(face_cascade_name)) {
        std::cerr << "--(!)Error loading" << std::endl;
        return EXIT_FAILURE;
    }
    if (!eyes_cascade.load(eyes_cascade_name)) {
        std::cerr << "--(!)Error loading" << std::endl;
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
