cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

option(built_dnn "Enabled if opencv is built dnn" OFF)
option(built_with_ade "Enabled if opencv is built with ade" OFF)
option(built_with_ffmpeg "Enabled if opencv is built with ffmpeg" OFF)
option(built_contrib_sfm "Enabled if opencv is built contrib sfm" OFF)

find_package(OpenCV REQUIRED imgcodecs highgui objdetect CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE
    opencv_imgcodecs
    opencv_highgui
    opencv_objdetect
    $<TARGET_NAME_IF_EXISTS:opencv_gapi>
    $<TARGET_NAME_IF_EXISTS:opencv_videoio>
    $<TARGET_NAME_IF_EXISTS:opencv_sfm>
)
if(built_dnn)
    target_link_libraries(${PROJECT_NAME} PRIVATE opencv_dnn)
endif()

target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
if(built_with_ade)
    target_compile_definitions(${PROJECT_NAME} PRIVATE BUILT_WITH_ADE)
endif()
if(built_with_ffmpeg)
    target_compile_definitions(${PROJECT_NAME} PRIVATE BUILT_WITH_FFMPEG)
endif()
if(built_contrib_sfm)
    target_compile_definitions(${PROJECT_NAME} PRIVATE BUILT_CONTRIB_SFM)
endif()
