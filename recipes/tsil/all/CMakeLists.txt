cmake_minimum_required(VERSION 3.4)
project(TSIL C)

include(conanbuildinfo.cmake)
conan_basic_setup()

set(SOURCE_DIR source_subfolder)

add_library(tsil
  ${SOURCE_DIR}/initialize.c
  ${SOURCE_DIR}/evaluate.c
  ${SOURCE_DIR}/fevaluate.c
  ${SOURCE_DIR}/generic.c
  ${SOURCE_DIR}/rk6.c
  ${SOURCE_DIR}/rk5.c
  ${SOURCE_DIR}/functions.c
  ${SOURCE_DIR}/dilog.c
  ${SOURCE_DIR}/trilog.c
  ${SOURCE_DIR}/dBds.c
  ${SOURCE_DIR}/dSds.c
  ${SOURCE_DIR}/dTds.c
  ${SOURCE_DIR}/dUds.c
  ${SOURCE_DIR}/dsMds.c
  ${SOURCE_DIR}/initB.c
  ${SOURCE_DIR}/initS.c
  ${SOURCE_DIR}/initT.c
  ${SOURCE_DIR}/initU.c
  ${SOURCE_DIR}/initV.c
  ${SOURCE_DIR}/initM.c
  ${SOURCE_DIR}/special.c
  ${SOURCE_DIR}/analyticAB.c
  ${SOURCE_DIR}/analyticI.c
  ${SOURCE_DIR}/analyticS.c
  ${SOURCE_DIR}/analyticT.c
  ${SOURCE_DIR}/analyticTbar.c
  ${SOURCE_DIR}/analyticU.c
  ${SOURCE_DIR}/analyticV.c
  ${SOURCE_DIR}/analyticM.c
  ${SOURCE_DIR}/setTbar.c
  ${SOURCE_DIR}/setV.c
  ${SOURCE_DIR}/setbold.c
  )

add_executable(tsil.x ${SOURCE_DIR}/basecalc.c)
target_link_libraries(tsil.x tsil m)
set_target_properties(tsil.x PROPERTIES OUTPUT_NAME "tsil")

set(size long CACHE STRING "set floating point data size")
set_property(CACHE size PROPERTY STRINGS long double)

if(size STREQUAL "double")
  target_compile_definitions(tsil PUBLIC TSIL_SIZE_DOUBLE)
elseif(size STREQUAL "long")
  target_compile_definitions(tsil PUBLIC TSIL_SIZE_LONG)
else()
  message(FATAL_ERROR "You must set size to either double or long")
endif()

message(STATUS "Using size: ${size}")

install(
  FILES
    "${SOURCE_DIR}/tsil.h"
    "${SOURCE_DIR}/tsil_cpp.h"
  DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
)

install(
  TARGETS tsil tsil.x
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
