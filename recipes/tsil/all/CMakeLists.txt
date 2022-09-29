cmake_minimum_required(VERSION 3.4)
project(TSIL LANGUAGES C)

add_library(tsil
  ${TSIL_SRC_DIR}/initialize.c
  ${TSIL_SRC_DIR}/evaluate.c
  ${TSIL_SRC_DIR}/fevaluate.c
  ${TSIL_SRC_DIR}/generic.c
  ${TSIL_SRC_DIR}/rk6.c
  ${TSIL_SRC_DIR}/rk5.c
  ${TSIL_SRC_DIR}/functions.c
  ${TSIL_SRC_DIR}/dilog.c
  ${TSIL_SRC_DIR}/trilog.c
  ${TSIL_SRC_DIR}/dBds.c
  ${TSIL_SRC_DIR}/dSds.c
  ${TSIL_SRC_DIR}/dTds.c
  ${TSIL_SRC_DIR}/dUds.c
  ${TSIL_SRC_DIR}/dsMds.c
  ${TSIL_SRC_DIR}/initB.c
  ${TSIL_SRC_DIR}/initS.c
  ${TSIL_SRC_DIR}/initT.c
  ${TSIL_SRC_DIR}/initU.c
  ${TSIL_SRC_DIR}/initV.c
  ${TSIL_SRC_DIR}/initM.c
  ${TSIL_SRC_DIR}/special.c
  ${TSIL_SRC_DIR}/analyticAB.c
  ${TSIL_SRC_DIR}/analyticI.c
  ${TSIL_SRC_DIR}/analyticS.c
  ${TSIL_SRC_DIR}/analyticT.c
  ${TSIL_SRC_DIR}/analyticTbar.c
  ${TSIL_SRC_DIR}/analyticU.c
  ${TSIL_SRC_DIR}/analyticV.c
  ${TSIL_SRC_DIR}/analyticM.c
  ${TSIL_SRC_DIR}/setTbar.c
  ${TSIL_SRC_DIR}/setV.c
  ${TSIL_SRC_DIR}/setbold.c
)

find_library(LIBM NAMES m)
target_link_libraries(tsil PRIVATE $<$<BOOL:${LIBM}>:${LIBM}>)

set(TSIL_SIZE long CACHE STRING "set floating point data size")
set_property(CACHE TSIL_SIZE PROPERTY STRINGS long double)

if(TSIL_SIZE STREQUAL "double")
  target_compile_definitions(tsil PUBLIC TSIL_SIZE_DOUBLE)
elseif(TSIL_SIZE STREQUAL "long")
  target_compile_definitions(tsil PUBLIC TSIL_SIZE_LONG)
else()
  message(FATAL_ERROR "You must set size to either double or long")
endif()

message(STATUS "Using size: ${TSIL_SIZE}")

install(
  FILES
    "${TSIL_SRC_DIR}/tsil.h"
    "${TSIL_SRC_DIR}/tsil_cpp.h"
  DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
)

install(
  TARGETS tsil
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

add_executable(tsil.x ${TSIL_SRC_DIR}/basecalc.c)
target_link_libraries(tsil.x PRIVATE tsil)
set_target_properties(tsil.x PROPERTIES OUTPUT_NAME "tsil" RUNTIME_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}/bin")

install(TARGETS tsil.x DESTINATION ${CMAKE_INSTALL_BINDIR})
