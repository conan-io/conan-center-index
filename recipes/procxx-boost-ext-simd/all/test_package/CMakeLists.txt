cmake_minimum_required(VERSION 3.1.0)
project(test_package)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

find_package(Boost.SIMD REQUIRED)

# FIXME: components from Boost.SIMD (target Boost::SIMD) don't work.
# It should be:
# find_package(BOOST REQUIRED COMPONENTS SIMD)
# See https://github.com/conan-io/conan-center-index/issues/6682 for details.
find_package(Boost REQUIRED COMPONENTS date_time) #  COMPONENTS SIMD)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} Boost::headers Boost::SIMD)
# FIXME: recipe should transitively sets proper minimum cxx standard.
# See https://github.com/conan-io/conan/issues/7772 about revising cxx std model.
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
