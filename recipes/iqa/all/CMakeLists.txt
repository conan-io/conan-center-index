cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(MSVC AND BUILD_SHARED_LIBS)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

file(GLOB IQA_SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/source/*.c)
file(GLOB IQA_HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/include/*.h)

add_library(iqa ${IQA_SOURCES})
target_include_directories(iqa PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/include)

install(TARGETS iqa
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)
install(FILES ${IQA_HEADERS} DESTINATION include)
