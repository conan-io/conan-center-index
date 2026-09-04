cmake_minimum_required(VERSION 3.22)
project(test_package LANGUAGES CXX)

# The package ships CMake scripts. CPM sets COPACABANA_SOURCE_DIR when it adds the package;
# the test does the same by hand, then checks the tree defines what consumers call.
set(COPACABANA_SOURCE_DIR "${COPACABANA_SOURCE}/res")
include("${COPACABANA_SOURCE_DIR}/copacabana/cmake/copacabana.cmake")

if(NOT COMMAND copa_setup_install)
  message(FATAL_ERROR "copacabana.cmake did not define copa_setup_install")
endif()

add_executable(test_package test_package.cpp)
