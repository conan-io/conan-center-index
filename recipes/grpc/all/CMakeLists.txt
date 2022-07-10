cmake_minimum_required(VERSION 2.8.12)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

add_subdirectory("source_subfolder")

# TODO: move to a patch? It avoids link errors while resolving abseil symbols with gcc
if (TARGET check_epollexclusive)
    set_target_properties(check_epollexclusive PROPERTIES LINKER_LANGUAGE CXX)
endif()
