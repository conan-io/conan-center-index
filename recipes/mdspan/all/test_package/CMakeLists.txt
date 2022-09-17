cmake_minimum_required(VERSION 3.5)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(mdspan REQUIRED CONFIG)

if (mdspan_VERSION VERSION_EQUAL "0.1.0")
        add_executable(${PROJECT_NAME} test_package.cpp)
else()
        add_executable(${PROJECT_NAME} test_package_v040.cpp)
endif()
target_link_libraries(${PROJECT_NAME} PRIVATE std::mdspan)
if (MSVC)
	target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_20)
else()
	target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_14)
endif()
