cmake_minimum_required(VERSION 3.8)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Tesseract REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(TARGET Tesseract::libtesseract)
    target_link_libraries(${PROJECT_NAME} Tesseract::libtesseract)
else()
    target_link_libraries(${PROJECT_NAME} libtesseract)
endif()
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
