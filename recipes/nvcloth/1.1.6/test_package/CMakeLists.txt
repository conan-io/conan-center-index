cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(nvcloth REQUIRED nvcloth CONFIG)
find_package(PhysX REQUIRED PhysX PhysXExtensions CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} nvcloth::nvcloth)
target_link_libraries(${PROJECT_NAME} PhysX::PhysX PhysX::PhysXExtensions)
