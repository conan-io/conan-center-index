cmake_minimum_required(VERSION 3.1)
project(PackageTest)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(MPI
    REQUIRED
    COMPONENTS
        C CXX
)

add_executable(${PROJECT_NAME} ${CMAKE_CURRENT_SOURCE_DIR}/example.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

