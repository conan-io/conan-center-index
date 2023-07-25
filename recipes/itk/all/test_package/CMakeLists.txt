cmake_minimum_required(VERSION 3.15)

project(test_package CXX)

find_package(ITK REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ITKCommon)
#itksys is already linked through dependencies of ITKCommon but we also want to check name alias
target_link_libraries(${PROJECT_NAME} PRIVATE ITK::itksys)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
