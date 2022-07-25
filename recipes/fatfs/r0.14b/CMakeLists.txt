cmake_minimum_required(VERSION 3.23)
project(fatfs LANGUAGES C)

set(FF_FS_READONLY 0 CACHE BOOL "")
set(FF_FS_MINIMIZE 0 CACHE STRING "")
set(FF_USE_FIND 0 CACHE STRING "")
set(FF_USE_MKFS 0 CACHE BOOL "")
set(FF_USE_FASTSEEK 0 CACHE BOOL "")
set(FF_USE_EXPAND 0 CACHE BOOL "")
set(FF_USE_CHMOD 0 CACHE BOOL "")
set(FF_USE_LABEL 0 CACHE BOOL "")
set(FF_USE_FORWARD 0 CACHE BOOL "")
set(FF_USE_STRFUNC 0 CACHE STRING "")
set(FF_PRINT_LLI 0 CACHE BOOL "")
set(FF_PRINT_FLOAT 0 CACHE STRING "")
set(FF_STRF_ENCODE 0 CACHE STRING "")
set(FF_CODE_PAGE 0 CACHE STRING "")
set(FF_USE_LFN 0 CACHE STRING "")
set(FF_MAX_LFN 255 CACHE STRING "")
set(FF_LFN_UNICODE 0 CACHE STRING "")
set(FF_LFN_BUF 255 CACHE STRING "")
set(FF_SFN_BUF 12 CACHE STRING "")
set(FF_FS_RPATH 0 CACHE STRING "")
set(FF_VOLUMES 1 CACHE STRING "")
set(FF_STR_VOLUME_ID 0 CACHE STRING "")
set(FF_VOLUME_STRS "\"RAM\",\"NAND\",\"CF\",\"SD\",\"SD2\",\"USB\",\"USB2\",\"USB3\"" CACHE STRING "")
set(FF_MULTI_PARTITION 0 CACHE BOOL "")
set(FF_MIN_SS 512 CACHE STRING "")
set(FF_MAX_SS 512 CACHE STRING "")
set(FF_LBA64 0 CACHE BOOL "")
set(FF_MIN_GPT 0x10000000 CACHE STRING "")
set(FF_USE_TRIM 0 CACHE BOOL "")
set(FF_FS_TINY 0 CACHE BOOL "")
set(FF_FS_EXFAT 0 CACHE BOOL "")
set(FF_FS_NORTC 0 CACHE BOOL "")
set(FF_NORTC_MON 1 CACHE STRING "")
set(FF_NORTC_MDAY 1 CACHE STRING "")
set(FF_NORTC_YEAR 2020 CACHE STRING "")
set(FF_FS_NOFSINFO 0 CACHE STRING "")
set(FF_FS_LOCK 0 CACHE STRING "")
set(FF_FS_REENTRANT 0 CACHE BOOL "")
set(FF_FS_TIMEOUT 1000 CACHE STRING "")

configure_file(ffconf.h.in
               ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/include/ffconf.h)
file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/source/ff.h
          ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/source/diskio.h
     DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/include)
file(
  REMOVE
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/source/ffconf.h
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/source/ff.h
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/source/diskio.h
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/source/diskio.c
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/source/ffsystem.c)

add_library(${PROJECT_NAME})
target_sources(${PROJECT_NAME} PRIVATE source_subfolder/source/ff.c
                                       source_subfolder/source/ffunicode.c)
target_sources(
  ${PROJECT_NAME}
  PUBLIC FILE_SET
         HEADERS
         BASE_DIRS
         source_subfolder/include
         FILES
         source_subfolder/include/ffconf.h
         source_subfolder/include/ff.h
         source_subfolder/include/diskio.h)
target_include_directories(${PROJECT_NAME} PUBLIC source_subfolder/include)

include(GNUInstallDirs)
install(
  TARGETS ${PROJECT_NAME}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  FILE_SET HEADERS DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/fatfs)
