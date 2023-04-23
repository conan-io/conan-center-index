cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX) # if the project uses c++

find_package(samurai REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)

# don't link to ${CONAN_LIBS} or CONAN_PKG::package
target_link_libraries(${PROJECT_NAME} PRIVATE samurai::samurai)

# In case the target project need a specific C++ standard
# target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
