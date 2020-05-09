cmake_minimum_required (VERSION 3.5)

# https://cmake.org/cmake/help/latest/variable/CMAKE_OSX_DEPLOYMENT_TARGET.html
set(CMAKE_OSX_DEPLOYMENT_TARGET "10.9" CACHE STRING "Minimum OS X deployment version")

project (VCVRackSDKTest)

set (LIB_NAME plugintest)
set (CMAKE_CXX_STANDARD 11)

include(${CMAKE_BINARY_DIR}/../conanbuildinfo.cmake)
conan_basic_setup()

add_library(${LIB_NAME} MODULE plugintest.cpp)

target_link_libraries(plugintest ${CONAN_LIBS})

if (CMAKE_CXX_COMPILER_ID STREQUAL "AppleClang")
  set_target_properties(${LIB_NAME} PROPERTIES SUFFIX ".dylib")
endif ()
