function(zserio_generate_cpp GENERATED_SOURCES_OUT)
    find_program(JAVA java)
    if (NOT JAVA)
        message(FATAL_ERROR "Could not find java!")
    endif()
    if (NOT DEFINED ENV{ZSERIO_JAR_FILE} OR NOT EXISTS $ENV{ZSERIO_JAR_FILE})
        message(FATAL_ERROR "Could not fine zserio.jar!")
    endif()

    cmake_parse_arguments(ZSERIO_COMPILER
        "IS_DEFAULT_PACKAGE"
        "MAIN_ZS;SRC_DIR;GEN_DIR"
        "EXTRA_ARGS"
        ${ARGN})

    # check required arguments
    foreach (ARG MAIN_ZS GEN_DIR)
        if (NOT DEFINED ZSERIO_COMPILER_${ARG})
            message(FATAL_ERROR "No value defined for required argument ${ARG}!")
        endif ()
    endforeach ()

    # default values
    if (NOT DEFINED ZSERIO_COMPILER_SRC_DIR)
        set(ZSERIO_COMPILER_SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}")
    endif ()

    execute_process(
        COMMAND ${JAVA} -jar $ENV{ZSERIO_JAR_FILE} -src ${ZSERIO_COMPILER_SRC_DIR}
            ${ZSERIO_COMPILER_MAIN_ZS} -cpp ${ZSERIO_COMPILER_GEN_DIR} ${ZSERIO_COMPILER_EXTRA_ARGS}
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    )

    file(GLOB_RECURSE GENERATED_SOURCES RELATIVE "${CMAKE_CURRENT_BINARY_DIR}"
        "${ZSERIO_COMPILER_GEN_DIR}/*.h"
        "${ZSERIO_COMPILER_GEN_DIR}/*.cpp")

    set_source_files_properties(${GENERATED_SOURCES} PROPERTIES GENERATED TRUE)
    set(${GENERATED_SOURCES_OUT} ${GENERATED_SOURCES} PARENT_SCOPE)
endfunction()

