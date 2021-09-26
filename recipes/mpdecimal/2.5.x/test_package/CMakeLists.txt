cmake_minimum_required(VERSION 3.1)
project(test_package)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

# This is a non-official mpdecimal module!
find_package(mpdecimal REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE mpdecimal::libmpdecimal)

if(MPDECIMAL_CXX    )
    add_executable(${PROJECT_NAME}_cpp test_package.cpp)
    set_propertY(TARGET ${PROJECT_NAME}_cpp PROPERTY CXX_STANDARD 11)
    target_link_libraries(${PROJECT_NAME}_cpp PRIVATE mpdecimal::libmpdecimal++)
endif()
