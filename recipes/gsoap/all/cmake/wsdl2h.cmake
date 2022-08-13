
# Generate project for wsdl2h

set(WSDL2H_PATH ${CMAKE_SOURCE_DIR}/${GSOAP_PATH}/gsoap/wsdl)

set(SRC_CPP
    ${WSDL2H_PATH}/wsdl2h.cpp
    ${WSDL2H_PATH}/wsdl.cpp
    ${WSDL2H_PATH}/wadl.cpp
    ${WSDL2H_PATH}/schema.cpp
    ${WSDL2H_PATH}/soap.cpp
    ${WSDL2H_PATH}/mime.cpp
    ${WSDL2H_PATH}/wsp.cpp
    ${WSDL2H_PATH}/bpel.cpp
    ${WSDL2H_PATH}/types.cpp
    ${WSDL2H_PATH}/service.cpp
    ${WSDL2H_PATH}/../stdsoap2.cpp
    ${CMAKE_BINARY_DIR}/generated/wsdlC.cpp
    )

if(${WITH_OPENSSL})
    list(APPEND SRC_CPP
         ${GSOAP_PATH}/gsoap/plugin/httpda.c
         ${GSOAP_PATH}/gsoap/plugin/smdevp.c
         ${GSOAP_PATH}/gsoap/plugin/threads.c
        )
endif()

set_source_files_properties(${SRC_CPP} PROPERTIES LANGUAGE CXX)
set_source_files_properties(${CMAKE_BINARY_DIR}/generated/wsdlC.cpp PROPERTIES GENERATED TRUE)

# Search for soapcpp2 executable
if(CMAKE_CROSSCOMPILING)
    find_program(SOAPCPP2_PROGRAM soapcpp2 PATHS ENV PATH NO_DEFAULT_PATH)
endif()
if(NOT SOAPCPP2_PROGRAM)
    set(SOAPCPP2_PROGRAM $<TARGET_FILE:soapcpp2>)
endif()

add_custom_command(
    OUTPUT ${CMAKE_BINARY_DIR}/generated/wsdlC.cpp
    COMMAND ${SOAPCPP2_PROGRAM} -I${GSOAP_PATH}/gsoap/import -SC -pwsdl -d${CMAKE_BINARY_DIR}/generated ${WSDL2H_PATH}/wsdl.h
    COMMENT "Parsing WSDL and Schema definitions"
    WORKING_DIRECTORY ${WSDL2H_PATH}
    )

add_custom_target(WSDL2H_GENERATORS
    DEPENDS
        ${CMAKE_BINARY_DIR}/generated/wsdlC.cpp)

add_executable(wsdl2h ${SRC_CPP})
target_include_directories(wsdl2h
    PRIVATE ${GSOAP_PATH}/gsoap
    PRIVATE ${CMAKE_BINARY_DIR}/generated
    PRIVATE ${WSDL2H_PATH})
add_dependencies(wsdl2h WSDL2H_GENERATORS)
if(${WITH_OPENSSL})
    find_package(ZLIB REQUIRED)
    target_include_directories(wsdl2h PRIVATE ${GSOAP_PATH}/gsoap/plugin)
    target_compile_definitions(wsdl2h PRIVATE WITH_OPENSSL WITH_GZIP)
    target_link_libraries(wsdl2h OpenSSL::Crypto OpenSSL::SSL ZLIB::ZLIB)
endif()

install(TARGETS wsdl2h DESTINATION ${CMAKE_INSTALL_BINDIR})
