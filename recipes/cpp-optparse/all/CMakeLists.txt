cmake_minimum_required(VERSION 3.13)
project(cpp-optparser)

include(${CMAKE_CURRENT_BINARY_DIR}/../conanbuildinfo.cmake)
conan_basic_setup()

add_library(OptionParser ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/OptionParser.cpp)

target_include_directories(OptionParser PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder)

conan_target_link_libraries(OptionParser)

install(TARGETS OptionParser
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib)

install(DIRECTORY source_subfolder/
        DESTINATION include
        FILES_MATCHING
        PATTERN "*.h")
