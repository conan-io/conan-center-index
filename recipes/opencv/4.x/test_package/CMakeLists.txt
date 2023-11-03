cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

enable_testing()

set(TESTED_MODULES
    # Main modules
    "calib3d" "core" "dnn" "features2d" "flann" "gapi" "highgui" "imgcodecs"
    "imgproc" "ml" "objdetect" "photo" "stitching" "video" "videoio"
    # Extra modules
    "alphamat" "aruco" "bgsegm" "bioinspired" "ccalib" "datasets" "dnn_superres"
    "face" "freetype" "fuzzy" "hdf" "hfs" "img_hash" "intensity_transform"
    "line_descriptor" "mcc" "optflow" "phase_unwrapping" "plot" "quality" "reg"
    "rgbd" "saliency" "sfm" "shape" "structured_light" "superres"
    "surface_matching" "text" "tracking" "wechat_qrcode" "xfeatures2d"
    "ximgproc" "xobjdetect" "xphoto"
)

find_package(OpenCV REQUIRED core CONFIG)

foreach(_module ${TESTED_MODULES})
    string(TOUPPER ${_module} _module_upper)
    if(OPENCV_WITH_${_module_upper})
        set(_test_target test_${_module})
        set(_module_target opencv_${_module})
        add_executable(${_test_target} ${_test_target}.cpp)
        target_link_libraries(${_test_target} PRIVATE ${_module_target})
        target_compile_features(${_test_target} PRIVATE cxx_std_11)
        if(NOT ${_module} STREQUAL "highgui")
            add_test(NAME ${_test_target} COMMAND ${_test_target})
        endif()
    endif()
endforeach()
