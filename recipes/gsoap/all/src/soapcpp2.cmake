
# Generate project for soapcpp2 executable

set(STDCPP2_PATH ${CMAKE_SOURCE_DIR}/${GSOAP_PATH}/gsoap/src)

set(SRC_CPP
    ${STDCPP2_PATH}/symbol2.c
    ${STDCPP2_PATH}/error2.c
    ${STDCPP2_PATH}/init2.c
    ${STDCPP2_PATH}/soapcpp2.c
    ${CMAKE_BINARY_DIR}/generated/soapcpp2_yacc.tab.c
    ${CMAKE_BINARY_DIR}/generated/lex.yy.c
    )
set_source_files_properties(${CMAKE_BINARY_DIR}/generated/soapcpp2_yacc.tab.c PROPERTIES GENERATED TRUE)
set_source_files_properties(${CMAKE_BINARY_DIR}/generated/soapcpp2_yacc.tab.h PROPERTIES GENERATED TRUE)
set_source_files_properties(${CMAKE_BINARY_DIR}/generated/lex.yy.c PROPERTIES GENERATED TRUE)

# Create the generated folder
add_custom_target(create-generated-folder ALL
    COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_BINARY_DIR}/generated)

if(WIN32)
    add_custom_command(
        OUTPUT ${CMAKE_BINARY_DIR}/generated/soapcpp2_yacc.tab.c
        COMMAND ${CONAN_WINFLEXBISON_ROOT}/bin/win_bison.exe -d -v -o ${CMAKE_BINARY_DIR}/generated/soapcpp2_yacc.tab.c ${STDCPP2_PATH}/soapcpp2_yacc.y
        COMMENT "Run BISON on soapcpp2"
    )

    add_custom_command(
        OUTPUT ${CMAKE_BINARY_DIR}/generated/lex.yy.c
        COMMAND ${CONAN_WINFLEXBISON_ROOT}/bin/win_flex.exe -o ${CMAKE_BINARY_DIR}/generated/lex.yy.c ${STDCPP2_PATH}/soapcpp2_lex.l
        COMMENT "Run FLEX on soapcpp2"
    )

else()
    add_custom_command(
        OUTPUT ${CMAKE_BINARY_DIR}/generated/soapcpp2_yacc.tab.c
        COMMAND ${CONAN_BISON_ROOT}/bin/yacc -d -v -o ${CMAKE_BINARY_DIR}/generated/soapcpp2_yacc.tab.c ${STDCPP2_PATH}/soapcpp2_yacc.y
        COMMENT "Run YACC on soapcpp2"
    )

    add_custom_command(
        OUTPUT ${CMAKE_BINARY_DIR}/generated/lex.yy.c
        COMMAND ${CONAN_FLEX_ROOT}/bin/flex -o ${CMAKE_BINARY_DIR}/generated/lex.yy.c ${STDCPP2_PATH}/soapcpp2_lex.l
        COMMENT "Run FLEX on soapcpp2"
    )
endif()

add_custom_target(FLEXBISON_GENERATORS
    DEPENDS
        ${CMAKE_BINARY_DIR}/generated/soapcpp2_yacc.tab.c
        ${CMAKE_BINARY_DIR}/generated/lex.yy.c)


add_dependencies(FLEXBISON_GENERATORS create-generated-folder)

add_executable(soapcpp2 ${SRC_CPP})
target_include_directories(soapcpp2 PRIVATE ${STDCPP2_PATH})
set_source_files_properties(${SRC_CPP} PROPERTIES LANGUAGE C)
add_dependencies(soapcpp2 FLEXBISON_GENERATORS)
install(TARGETS soapcpp2 RUNTIME DESTINATION bin)
