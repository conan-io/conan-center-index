cmake_minimum_required(VERSION 3.4)
project(easyexif)

set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_CXX_STANDARD 11)

if(WIN32 AND BUILD_SHARED_LIBS)
  set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

add_library(easyexif exif.cpp)
target_include_directories(easyexif PUBLIC exif.h)

install(TARGETS easyexif
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib)
install(FILES exif.h DESTINATION include/easyexif)

