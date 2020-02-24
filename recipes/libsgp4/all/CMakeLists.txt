cmake_minimum_required(VERSION 3.4.3)
project(libsgp4)

include(conanbuildinfo.cmake)
conan_basic_setup()

set(LIBSGP4_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/libsgp4)

add_library(libsgp4
  ${LIBSGP4_SOURCE_DIR}/CoordGeodetic.cc
  ${LIBSGP4_SOURCE_DIR}/CoordTopocentric.cc
  ${LIBSGP4_SOURCE_DIR}/DateTime.cc
  ${LIBSGP4_SOURCE_DIR}/DecayedException.cc
  ${LIBSGP4_SOURCE_DIR}/Eci.cc
  ${LIBSGP4_SOURCE_DIR}/Globals.cc
  ${LIBSGP4_SOURCE_DIR}/Observer.cc
  ${LIBSGP4_SOURCE_DIR}/OrbitalElements.cc
  ${LIBSGP4_SOURCE_DIR}/SGP4.cc
  ${LIBSGP4_SOURCE_DIR}/SatelliteException.cc
  ${LIBSGP4_SOURCE_DIR}/SolarPosition.cc
  ${LIBSGP4_SOURCE_DIR}/TimeSpan.cc
  ${LIBSGP4_SOURCE_DIR}/Tle.cc
  ${LIBSGP4_SOURCE_DIR}/TleException.cc
  ${LIBSGP4_SOURCE_DIR}/Util.cc
  ${LIBSGP4_SOURCE_DIR}/Vector.cc
)

set_target_properties(libsgp4 PROPERTIES CXX_STANDARD 11)

if(WIN32 AND BUILD_SHARED_LIBS)
  set_target_properties(libsgp4 PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
endif()

install(
  TARGETS libsgp4
  EXPORT libsgp4
  RUNTIME DESTINATION bin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
)

set(INCS
  ${LIBSGP4_SOURCE_DIR}/CoordGeodetic.h
  ${LIBSGP4_SOURCE_DIR}/CoordTopocentric.h
  ${LIBSGP4_SOURCE_DIR}/DateTime.h
  ${LIBSGP4_SOURCE_DIR}/DecayedException.h
  ${LIBSGP4_SOURCE_DIR}/Eci.h
  ${LIBSGP4_SOURCE_DIR}/Globals.h
  ${LIBSGP4_SOURCE_DIR}/Observer.h
  ${LIBSGP4_SOURCE_DIR}/OrbitalElements.h
  ${LIBSGP4_SOURCE_DIR}/SatelliteException.h
  ${LIBSGP4_SOURCE_DIR}/SGP4.h
  ${LIBSGP4_SOURCE_DIR}/SolarPosition.h
  ${LIBSGP4_SOURCE_DIR}/TimeSpan.h
  ${LIBSGP4_SOURCE_DIR}/TleException.h
  ${LIBSGP4_SOURCE_DIR}/Tle.h
  ${LIBSGP4_SOURCE_DIR}/Util.h
  ${LIBSGP4_SOURCE_DIR}/Vector.h
)

install(FILES ${INCS} DESTINATION include/libsgp4)
