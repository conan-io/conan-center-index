cmake_minimum_required(VERSION 3.8)

project(test_package CXX)

find_package(qpdf REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE qpdf::libqpdf)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
# msvc has problems consuming #warning macro
# therefore we need a code-path in the include avoiding this warning https://github.com/qpdf/qpdf/issues/804
target_compile_definitions(${PROJECT_NAME} PUBLIC POINTERHOLDER_TRANSITION=4)
