cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(Tesseract REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(TARGET Tesseract::libtesseract)
    target_link_libraries(${PROJECT_NAME} PRIVATE Tesseract::libtesseract)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE libtesseract)
endif()
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
