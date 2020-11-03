cmake_minimum_required(VERSION 3.13)
project(cpp-optparser)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_library(OptionParser source_subfolder/OptionParser.cpp)

target_include_directories(OptionParser PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder)

conan_target_link_libraries(OptionParser)

install(TARGETS OptionParser
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib)

install(FILES source_subfolder/OptionParser.h DESTINATION include)

if(WIN32)
    if(BUILD_SHARED_LIBS)
        set_target_properties(OptionParser PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
    endif()
endif()
