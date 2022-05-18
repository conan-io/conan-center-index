cmake_minimum_required(VERSION 3.15)
project(test_tool_requires CXX)

add_library(test_tool_requires src/test_tool_requires.cpp)
target_include_directories(test_tool_requires PUBLIC include)

set_target_properties(test_tool_requires PROPERTIES PUBLIC_HEADER "include/test_tool_requires.h")
install(TARGETS test_tool_requires)
