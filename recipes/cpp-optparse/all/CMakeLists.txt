cmake_minimum_required(VERSION 3.4)
project(cpp-optparser)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_library(OptionParser source_subfolder/OptionParser.cpp)

if(MSVC AND BUILD_SHARED_LIBS)
    set_target_properties(OptionParser PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
endif()

install(TARGETS OptionParser
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib)

install(FILES source_subfolder/OptionParser.h DESTINATION include)
