
# Use the following function to generate C source files from flatbuffer definition files:
#
# flatcc_generate_sources(GENERATED_SOURCE_DIRECTORY <directory where to write source files>
#                         GENERATE_BUILDER
#                         GENERATE_VERIFIER
#                         EXPECTED_OUTPUT_FILES <list of files that flatcc is supposed to generate>
#                         DEFINITION_FILES <list of flatbuffer definition files (.fbs)>
# )
#
# GENERATE_BUILDER and GENERATE_VERIFIER are boolean options. When specified they will instruct
# flatcc to generate builder / verifier source code.
#
# With cross-compiling you should provide the directory where the flatcc compiler executable is located
# in environment variable FLATCC_BUILD_BIN_PATH. If you use Conan and add flatcc as a build requirement
# this will be done automatically.


function(flatcc_generate_sources)

    # parse function arguments
    set(OUTPREFIX "FLATCC") #variables created by 'cmake_parse_arguments' will be prefixed with this
    set(NO_VAL_ARGS GENERATE_BUILDER GENERATE_VERIFIER)
    set(SINGLE_VAL_ARGS GENERATED_SOURCE_DIRECTORY)
    set(MULTI_VAL_ARGS DEFINITION_FILES EXPECTED_OUTPUT_FILES CC_OPTIONS)

    cmake_parse_arguments(${OUTPREFIX}
                          "${NO_VAL_ARGS}"
                          "${SINGLE_VAL_ARGS}"
                          "${MULTI_VAL_ARGS}"
                          ${ARGN}
    )
    if (GENERATED_SOURCE_DIRECTORY IN_LIST FLATCC_KEYWORDS_MISSING_VALUES)
        message(FATAL_ERROR "No directory provided after GENERATED_SOURCE_DIRECTORY keyword")
    endif()
    if (NOT FLATCC_GENERATED_SOURCE_DIRECTORY)
        set(FLATCC_GENERATED_SOURCE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})
    endif()
    message(STATUS "Flatcc sources will be generated in directory ${FLATCC_GENERATED_SOURCE_DIRECTORY}")

    if (FLATCC_GENERATE_BUILDER)
        list(APPEND FLATCC_CC_OPTIONS --builder)
    endif()
    if (FLATCC_GENERATE_VERIFIER)
        list(APPEND FLATCC_CC_OPTIONS --verifier)
    endif()

    if (FLATCC_DEFINITION_FILES)
        if (NOT EXISTS ${FLATCC_GENERATED_SOURCE_DIRECTORY})
            file(MAKE_DIRECTORY ${FLATCC_GENERATED_SOURCE_DIRECTORY})
        endif()

        message(VERBOSE "Executing command ${FLATCC_COMPILER} ${FLATCC_CC_OPTIONS} -o ${FLATCC_GENERATED_SOURCE_DIRECTORY} ${FLATCC_DEFINITION_FILES}")
        add_custom_command(OUTPUT ${FLATCC_EXPECTED_OUTPUT_FILES}
                           COMMAND ${FLATCC_COMPILER} ${FLATCC_CC_OPTIONS} -o ${FLATCC_GENERATED_SOURCE_DIRECTORY} ${FLATCC_DEFINITION_FILES}
                           WORKING_DIRECTORY ${FLATCC_GENERATED_SOURCE_DIRECTORY})
    else()
        message(WARNING "No flatbuffer definition files provided, no sources will be generated")
    endif()

endfunction()


#### Main ####

#When cross-compiling user can provide location of the flatbuffers to C compiler in build arch via
#environment variable FLATCC_BUILD_BIN_PATH
set(FLATCC_BIN_PATH "$ENV{FLATCC_BUILD_BIN_PATH}")
if (FLATCC_BIN_PATH)
    #user provided location where asn1c compiler executable is installed
    find_program(FLATCC_COMPILER flatcc
                 PATHS ${FLATCC_BIN_PATH}
                 NO_DEFAULT_PATH
                 NO_SYSTEM_ENVIRONMENT_PATH
                 NO_CMAKE_SYSTEM_PATH
)
else()
    #Find compiler exe in current install location
    find_program(FLATCC_COMPILER flatcc
                NO_SYSTEM_ENVIRONMENT_PATH
                NO_CMAKE_SYSTEM_PATH
    )
endif()


if (NOT FLATCC_COMPILER)
    message(FATAL_ERROR "Could not locate the flatcc compiler executable")
endif()
