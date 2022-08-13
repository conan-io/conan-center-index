cmake_minimum_required(VERSION 3.0)
project(gSOAP)

include(GNUInstallDirs)

option(BUILD_TOOLS "Build soapcpp2 and wsdl2h" ON)
option(BUILD_GSOAP "Build gsoap library" ON)

message("Generate gSOAP from sources at ${GSOAP_PATH}")

if(${WITH_OPENSSL})
  find_package(OpenSSL REQUIRED)
  find_package(ZLIB REQUIRED)
endif()

# Tools
if(${BUILD_TOOLS})
  include(${CMAKE_SOURCE_DIR}/cmake/soapcpp2.cmake)
  include(${CMAKE_SOURCE_DIR}/cmake/wsdl2h.cmake)

  install(FILES ${CMAKE_SOURCE_DIR}/${GSOAP_PATH}/gsoap/typemap.dat DESTINATION res)
  install(DIRECTORY ${CMAKE_SOURCE_DIR}/${GSOAP_PATH}/gsoap/import DESTINATION ${CMAKE_INSTALL_BINDIR}
          FILES_MATCHING PATTERN "*.h")
endif()

# Libraries
if(${BUILD_GSOAP})
  include(${CMAKE_SOURCE_DIR}/cmake/gsoap.cmake)
endif()
