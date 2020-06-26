cmake_minimum_required(VERSION 2.8)
project(svm C CXX)

include(${CMAKE_SOURCE_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_library(svm svm.cpp)
set_target_properties(svm PROPERTIES PUBLIC_HEADER svm.h)

add_executable(svm-predict svm-predict.c)
target_link_libraries(svm-predict svm)

add_executable(svm-train svm-train.c)
target_link_libraries(svm-train svm)

add_executable(svm-scale svm-scale.c)

install(TARGETS svm svm-predict svm-train svm-scale
        PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/svm
        )
