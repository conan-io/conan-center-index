cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

enable_testing()

find_package(OpenCV REQUIRED core CONFIG)

add_executable(test_core test_core.cpp)
target_link_libraries(test_core PRIVATE opencv_core)
target_compile_features(test_core PRIVATE cxx_std_11)
add_test(NAME test_core COMMAND test_core)

set(TESTED_OPENCV_MODULES
    # Main modules
    "calib3d" "features2d" "flann" "gapi" "highgui" "imgcodecs" "imgproc"
    "ml" "objdetect" "photo" "stitching" "video" "videoio"
    # Extra modules
    "alphamat" "aruco" "bgsegm" "bioinspired" "ccalib" "dnn_superres" "face"
    "freetype" "fuzzy" "hfs" "img_hash" "intensity_transform" "line_descriptor"
    "mcc" "optflow" "phase_unwrapping" "quality" "reg" "rgbd" "saliency" "sfm"
    "shape" "structured_light" "superres" "surface_matching" "text" "tracking"
    "wechat_qrcode" "xfeatures2d" "ximgproc" "xobjdetect" "xphoto"
)

foreach(_module ${TESTED_OPENCV_MODULES})
    string(TOUPPER ${_module} _module_upper)
    option(OPENCV_WITH_${_module_upper} "Enabled if opencv is built with ${_module} module" OFF)
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
