cmake_minimum_required(VERSION 3.8)

project(test_package CXX) # if the project uses c++

find_package(libpfm4 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} example.cpp)
# don't link to ${CONAN_LIBS} or CONAN_PKG::package
target_link_libraries(${PROJECT_NAME} PRIVATE libpfm4::libpfm4)
# In case the target project need a specific C++ standard
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
