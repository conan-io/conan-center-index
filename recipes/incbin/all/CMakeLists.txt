cmake_minimum_required(VERSION 3.15)
project(incbin_tool C)
add_executable(incbin_tool incbin.c)
install(TARGETS incbin_tool DESTINATION bin)
