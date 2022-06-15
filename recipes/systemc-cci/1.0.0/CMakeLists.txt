cmake_minimum_required(VERSION 3.8)

project(cci CXX C)

set(LIBRARY_VERSION_MAJOR 1 CACHE STRING "major version" FORCE)
set(LIBRARY_VERSION_MINOR 0 CACHE STRING "minor version" FORCE)
set(LIBRARY_VERSION_PATCH 0 CACHE STRING "minor version" FORCE)
set(LIBRARY_VERSION ${LIBRARY_VERSION_MAJOR}.${LIBRARY_VERSION_MINOR}.${LIBRARY_VERSION_PATCH} CACHE STRING "version" FORCE)

set(LIBRARY_NAME cciapi)

set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)

include(${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

if(DEFINED ENV{RAPIDJSON_HOME})
    set(RAPIDJSON $ENV{RAPIDJSON_HOME})
else()
	set(RAPIDJSON ${CMAKE_CURRENT_SOURCE_DIR}/packages/rapidjson)
endif()


FILE(GLOB CFG_HEADER_FILES src/cci_cfg/*.h )
FILE(GLOB CORE_HEADER_FILES src/cci_core/*.h )
FILE(GLOB UTILS_HEADER_FILES src/cci_utils/*.h )
set(SOURCES
	src/cci_cfg/cci_broker_handle.cpp
	src/cci_cfg/cci_broker_manager.cpp
	src/cci_cfg/cci_originator.cpp
	src/cci_cfg/cci_param_if.cpp
	src/cci_cfg/cci_param_untyped.cpp
	src/cci_cfg/cci_param_untyped_handle.cpp
	src/cci_cfg/cci_report_handler.cpp
	src/cci_core/cci_name_gen.cpp
	src/cci_core/cci_value_converter.cpp
	src/cci_core/cci_value.cpp
	src/cci_utils/broker.cpp
	src/cci_utils/consuming_broker.cpp
)

add_library(${LIBRARY_NAME} ${SOURCES})	
target_include_directories(${LIBRARY_NAME} PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_include_directories(${LIBRARY_NAME} PUBLIC ${RAPIDJSON}/include)

install(TARGETS ${LIBRARY_NAME}
  ARCHIVE DESTINATION lib COMPONENT libs   # static lib
  LIBRARY DESTINATION lib COMPONENT libs   # shared lib
  FRAMEWORK DESTINATION bin COMPONENT libs # for mac
  PUBLIC_HEADER DESTINATION include COMPONENT devel   # headers for mac (note the different component -> different package)
  INCLUDES DESTINATION include             # headers
  PUBLIC_HEADER DESTINATION include
)

install(FILES src/cci_configuration DESTINATION include)
install(FILES ${CFG_HEADER_FILES} DESTINATION include/cci_cfg)
install(FILES ${CORE_HEADER_FILES} DESTINATION include/cci_core)
install(FILES ${UTILS_HEADER_FILES} DESTINATION include/cci_utils)
