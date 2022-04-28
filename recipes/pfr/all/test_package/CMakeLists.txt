cmake_minimum_required(VERSION 3.1.0)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package_${PfrMajorVersion}.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

# PFR 1.0.4 doesn't support Visual Studio in C++14 mode, requires C++17.
# Otherwise, at least C++14 is required.
if (CMAKE_CXX_COMPILER_ID STREQUAL "MSVC" AND ${PfrMajorVersion} EQUAL 1)
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
    target_compile_definitions(${PROJECT_NAME} PRIVATE BOOST_PFR_USE_CPP17=1 BOOST_PFR_USE_LOOPHOLE=0)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
endif()
