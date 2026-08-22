cmake_minimum_required(VERSION 3.15)
project(easyexif)

include(GNUInstallDirs)

set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_CXX_STANDARD 11)

if(WIN32 AND BUILD_SHARED_LIBS)
  set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

add_library(easyexif ${EASYEXIF_SRC_DIR}/exif.cpp)
target_include_directories(easyexif PUBLIC ${EASYEXIF_SRC_DIR}/exif.h)
set_target_properties(
    easyexif
    PROPERTIES
    PUBLIC_HEADER "${EASYEXIF_SRC_DIR}/exif.h"
)

install(TARGETS easyexif
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/easyexif
)
