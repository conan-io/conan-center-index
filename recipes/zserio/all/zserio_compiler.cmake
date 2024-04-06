function(zserio_generate_cpp)
    find_program(JAVA java)
    if (NOT JAVA)
        message(FATAL_ERROR "Could not find java!")
    endif()
    if (NOT DEFINED ENV{ZSERIO_JAR_FILE} OR NOT EXISTS $ENV{ZSERIO_JAR_FILE})
        message(FATAL_ERROR "Could not fine zserio.jar!")
    endif()

    cmake_parse_arguments(ZSERIO_GENERATE
        ""
        "TARGET;SRC_DIR;MAIN_ZS;GEN_DIR"
        "EXTRA_ARGS"
        ${ARGN})

    # check required arguments
    foreach (ARG TARGET GEN_DIR)
        if (NOT DEFINED ZSERIO_GENERATE_${ARG})
            message(FATAL_ERROR "No value defined for required argument ${ARG}!")
        endif ()
    endforeach ()

    # default values
    if (NOT DEFINED ZSERIO_GENERATE_SRC_DIR)
        set(ZSERIO_GENERATE_SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}")
    endif ()
    if (NOT DEFINED ZSERIO_GENERATE_MAIN_ZS)
        # try to get a single main zs
        get_target_property(ZS_SOURCES ${ZSERIO_GENERATE_TARGET} SOURCES)
        list(FILTER ZS_SOURCES INCLUDE REGEX "\\.zs$")
        list(LENGTH ZS_SOURCES ZS_SOURCES_LENGTH)
        if (${ZS_SOURCES_LENGTH} EQUAL 1)
            list(GET ZS_SOURCES 0 ZSERIO_GENERATE_MAIN_ZS)
            message(STATUS "Found main '*.zs' file: '${ZSERIO_GENERATE_MAIN_ZS}'")
        else ()
            message(FATAL_ERROR "Main '*.zs* file not specifid and cannot be detected!")
        endif ()
    endif ()

    set(ZSERIO_COMMAND
        ${JAVA} -jar $ENV{ZSERIO_JAR_FILE}
            -src ${ZSERIO_GENERATE_SRC_DIR} ${ZSERIO_GENERATE_MAIN_ZS}
            -cpp ${ZSERIO_GENERATE_GEN_DIR}
            ${ZSERIO_GENERATE_EXTRA_ARGS}
    )

    # run the generator during configure phase, zserio has built in support to prevent sources re-generation
    # and thus it should't make problems when cmake reconfigure is triggered from another reason
    execute_process(
        COMMAND ${ZSERIO_COMMAND}
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        RESULT_VARIABLE ZSERIO_GENERATE_RESULT)

    if (NOT ${ZSERIO_GENERATE_RESULT} EQUAL 0)
        message(FATAL_ERROR "Zserio generator failed!")
    endif ()

    # ensure cmake reconfigure when zserio sources are changed
    file(GLOB_RECURSE ZSERIO_SOURCES RELATIVE "${CMAKE_CURRENT_SOURCE_DIR}"
        "${ZSERIO_GENERATE_SRC_DIR}/*.zs")
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS ${ZSERIO_SOURCES} $ENV{ZSERIO_JAR_FILE})

    file(GLOB_RECURSE GENERATED_SOURCES RELATIVE "${CMAKE_CURRENT_BINARY_DIR}"
        "${ZSERIO_GENERATE_GEN_DIR}/*.h"
        "${ZSERIO_GENERATE_GEN_DIR}/*.cpp")

    set_source_files_properties(${GENERATED_SOURCES} PROPERTIES GENERATED TRUE)
    target_sources(${ZSERIO_GENERATE_TARGET} PRIVATE ${GENERATED_SOURCES})
endfunction()
