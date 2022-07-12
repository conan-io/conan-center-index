cmake_minimum_required(VERSION 2.8.14)
project(ConanLemon C)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_executable(lemon source_subfolder/tool/lemon.c)
install(TARGETS lemon DESTINATION bin)
install(FILES source_subfolder/tool/lempar.c DESTINATION bin)
