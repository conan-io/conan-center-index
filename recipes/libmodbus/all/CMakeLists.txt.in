cmake_minimum_required(VERSION 3.1.2)

project(libmodbus C)
set(TARGET modbus)

set(LIBMODBUS_VERSION_MAJOR 3)
set(LIBMODBUS_VERSION_MINOR 1)
set(LIBMODBUS_VERSION_MICRO 4)
set(LIBMODBUS_VERSION "${LIBMODBUS_VERSION_MAJOR}.${LIBMODBUS_VERSION_MINOR}.${LIBMODBUS_VERSION_MICRO}")

if(WIN32)
  add_definitions(-D_CRT_SECURE_NO_WARNINGS)
endif()

configure_file(${CMAKE_SOURCE_DIR}/src/modbus-version.h.in
${CMAKE_SOURCE_DIR}/src/modbus-version.h)

include(${CMAKE_BINARY_DIR}/../conanbuildinfo.cmake)
conan_basic_setup()
include (CMakePackageConfigHelpers)

set(CURRENT_PUBLIC_HEADERS
    src/modbus.h
    src/modbus-rtu.h
    src/modbus-tcp.h
    src/modbus-version.h
   )

set(CURRENT_SRC
    src/modbus.c
    src/modbus-data.c
    src/modbus-private.h
    src/modbus-rtu.c
    src/modbus-rtu-private.h
    src/modbus-tcp.c
    src/modbus-tcp-private.h
    config.h
   )

   
set(LIB_PREFIX "lib")

if(BUILD_SHARED_LIBS)
  add_library(${TARGET} SHARED ${CURRENT_SRC} ${CURRENT_PUBLIC_HEADERS})
  target_compile_definitions(${TARGET} PRIVATE DLLBUILD)
  message(STATUS "${TARGET}: building SHARED library")
  if(WIN32)
    set(LIB_PREFIX "")
  endif()
else()
  add_library(${TARGET} STATIC ${CURRENT_SRC} ${CURRENT_PUBLIC_HEADERS})
  target_compile_definitions(${TARGET} PUBLIC LIBMODBUS_STATICBUILD)
  message(STATUS "${TARGET}: building STATIC library")
endif()

if(MSVC)
  target_link_libraries(${TARGET} ws2_32)
endif()

set_target_properties(${TARGET} 
  PROPERTIES
    PUBLIC_HEADER "${CURRENT_PUBLIC_HEADERS}"
    PREFIX "${LIB_PREFIX}"
    IMPORT_PREFIX "${LIB_PREFIX}"
    DEBUG_POSTFIX "_d"
  )

target_include_directories(${TARGET} PRIVATE .)

set(exportTarget "${CMAKE_PROJECT_NAME}-targets")
set(cmakeFilesInstallDir "cmake")
set(configFile "${CMAKE_BINARY_DIR}/${CMAKE_PROJECT_NAME}-config.cmake")
set(exportFileConfig "${cmakeFilesInstallDir}/${exportTarget}.cmake")
set(INCLUDE_INSTALL_DIR include/modbus)
get_target_property(LIB_NAMES ${TARGET} OUTPUT_NAME)

install(TARGETS ${TARGET}
        EXPORT ${exportTarget}
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
        RUNTIME DESTINATION bin
        PUBLIC_HEADER DESTINATION ${INCLUDE_INSTALL_DIR}
        )
        
configure_package_config_file (
    "${CMAKE_SOURCE_DIR}/project-config.cmake.in"
    ${configFile}
    INSTALL_DESTINATION ${cmakeFilesInstallDir}
    PATH_VARS exportFileConfig INCLUDE_INSTALL_DIR )
    
install (FILES ${configFile} DESTINATION ${cmakeFilesInstallDir})
install (EXPORT ${exportTarget} DESTINATION ${cmakeFilesInstallDir})
