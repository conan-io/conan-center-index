cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Drogon CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} Drogon::Drogon)

# drogon uses string_view when MSVC_VERSION is greater than 1900.
# https://github.com/drogonframework/drogon/blob/v1.7.5/lib/inc/drogon/utils/string_view.h#L16
if(DEFINED MSVC_VERSION AND MSVC_VERSION GREATER 1900)
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
endif()
