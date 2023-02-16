cmake_minimum_required(VERSION 3.8)
project(cci LANGUAGES CXX)

set(LIBRARY_NAME cciapi)

include(${CMAKE_CURRENT_SOURCE_DIR}/conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

find_package(RapidJSON REQUIRED CONFIG)
find_package(SystemCLanguage REQUIRED CONFIG)

set(SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/src")
set(CCI_CFG_DIR "${SOURCE_DIR}/cci_cfg")
set(CCI_CORE_DIR "${SOURCE_DIR}/cci_core")
set(CCI_UTILS_DIR "${SOURCE_DIR}/cci_utils")

set(SOURCES
    ${SOURCE_DIR}/cci_cfg/cci_broker_handle.cpp
    ${SOURCE_DIR}/cci_cfg/cci_broker_manager.cpp
    ${SOURCE_DIR}/cci_cfg/cci_originator.cpp
    ${SOURCE_DIR}/cci_cfg/cci_param_if.cpp
    ${SOURCE_DIR}/cci_cfg/cci_param_untyped.cpp
    ${SOURCE_DIR}/cci_cfg/cci_param_untyped_handle.cpp
    ${SOURCE_DIR}/cci_cfg/cci_report_handler.cpp
    ${SOURCE_DIR}/cci_core/cci_name_gen.cpp
    ${SOURCE_DIR}/cci_core/cci_value_converter.cpp
    ${SOURCE_DIR}/cci_core/cci_value.cpp
    ${SOURCE_DIR}/cci_utils/broker.cpp
    ${SOURCE_DIR}/cci_utils/consuming_broker.cpp
)

add_library(${LIBRARY_NAME} ${SOURCES})
target_include_directories(${LIBRARY_NAME} PRIVATE ${SOURCE_DIR})
target_link_libraries(${LIBRARY_NAME} PRIVATE RapidJSON::RapidJSON SystemC::SystemC)
set_target_properties(${LIBRARY_NAME} PROPERTIES
                      WINDOWS_EXPORT_ALL_SYMBOLS TRUE
                      VERSION ${CONAN_PACKAGE_VERSION})
target_compile_definitions(${LIBRARY_NAME} PRIVATE SC_INCLUDE_FX)

install(TARGETS ${LIBRARY_NAME}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})

install(DIRECTORY ${CCI_CFG_DIR} ${CCI_CORE_DIR} ${CCI_UTILS_DIR}
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
        FILES_MATCHING PATTERN "*.h")
install(FILES "${SOURCE_DIR}/cci_configuration" DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
