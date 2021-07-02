cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(mFAST REQUIRED mfast_xml_parser CONFIG)

FASTTYPEGEN_TARGET(Test Test.xml)
add_executable(${PROJECT_NAME} ${FASTTYPEGEN_Test_OUTPUTS} message_printer.cpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
if(MFAST_SHARED)
  target_link_libraries(${PROJECT_NAME} mfast_xml_parser)
else()
  target_link_libraries(${PROJECT_NAME} mfast_xml_parser_static)
endif()
