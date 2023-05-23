cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(mFAST REQUIRED mfast_xml_parser CONFIG)

FASTTYPEGEN_TARGET(Test Test.xml)
add_executable(${PROJECT_NAME} ${FASTTYPEGEN_Test_OUTPUTS} message_printer.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
if(TARGET mfast_xml_parser_static)
  target_link_libraries(${PROJECT_NAME} PRIVATE mfast_xml_parser_static)
else()
  target_link_libraries(${PROJECT_NAME} PRIVATE mfast_xml_parser)
endif()
