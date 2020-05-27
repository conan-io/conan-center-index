cmake_minimum_required(VERSION 3.1.0)
project(test_package)

include(${CMAKE_BINARY_DIR}/../conanbuildinfo.cmake)
conan_set_vs_runtime()
conan_set_libcxx()
conan_output_dirs_setup()

# Find includes in corresponding build directories
set(CMAKE_INCLUDE_CURRENT_DIR ON)
# Instruct CMake to run moc automatically when needed
set(CMAKE_AUTOMOC ON)
# Create code from a list of Qt designer ui files
set(CMAKE_AUTOUIC ON)

# Find the QtCore library
find_package(Qt5Core CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp greeter.h)
target_link_libraries(${PROJECT_NAME} Qt5::Core)

# configure_file(${CMAKE_CURRENT_BINARY_DIR}/qt.conf ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/qt.conf COPYONLY)
