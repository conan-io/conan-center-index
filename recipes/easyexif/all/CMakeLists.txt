cmake_minimum_required(VERSION 3.4)
project(easyexif)

set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_CXX_STANDARD 11)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(WIN32 AND BUILD_SHARED_LIBS)
  set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

set(SOURCE_SUBFOLDER "source_subfolder")

add_library(easyexif ${SOURCE_SUBFOLDER}/exif.cpp)
target_include_directories(easyexif PUBLIC ${SOURCE_SUBFOLDER}/exif.h)

install(TARGETS easyexif
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib)
install(FILES ${SOURCE_SUBFOLDER}/exif.h DESTINATION include/easyexif)

