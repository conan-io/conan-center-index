cmake_minimum_required(VERSION 3.0)
project(gSOAP)

option(BUILD_TOOLS "Build soapcpp2 and wsdl2h" ON)
option(BUILD_GSOAP "Build gsoap library" ON)

if(EXISTS "${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
  include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
else()
  include(conanbuildinfo.cmake)
endif()
conan_basic_setup()

message("Generate gSOAP from sources at ${GSOAP_PATH}")

# Tools
if(${BUILD_TOOLS})
  include(${CMAKE_SOURCE_DIR}/src/soapcpp2.cmake)
  include(${CMAKE_SOURCE_DIR}/src/wsdl2h.cmake)

  install(FILES ${CMAKE_SOURCE_DIR}/${GSOAP_PATH}/gsoap/typemap.dat DESTINATION res)
  install(DIRECTORY ${CMAKE_SOURCE_DIR}/${GSOAP_PATH}/gsoap/import DESTINATION .
          FILES_MATCHING PATTERN "*.h")
endif()

# Libraries
if(${BUILD_GSOAP})
  include(${CMAKE_SOURCE_DIR}/src/gsoap.cmake)
endif()
