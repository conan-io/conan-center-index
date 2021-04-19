cmake_minimum_required (VERSION 3.4)
set(CMAKE_OSX_DEPLOYMENT_TARGET "10.9" CACHE STRING "Minimum OS X deployment version")
project (huffman)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(MSVC)
    add_definitions (-D_WIN32_WINNT=0x0601)
    add_definitions (-D_SCL_SECURE_NO_WARNINGS=1)
    add_definitions (-D_CRT_SECURE_NO_WARNINGS=1)

    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /EHsc /utf-8")
endif()

if(WIN32 AND BUILD_SHARED_LIBS)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
    set(CMAKE_VS_INCLUDE_INSTALL_TO_DEFAULT_BUILD TRUE)
endif()

set(SRC
    source_subfolder/huffman.c
)

add_library(huffman ${SRC})

if(WIN32)
    target_link_libraries(huffman ws2_32)
endif()

INSTALL(TARGETS huffman
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib)

set(HEADERS
    source_subfolder/huffman.h
)

INSTALL(FILES ${HEADERS} DESTINATION include/huffman)
