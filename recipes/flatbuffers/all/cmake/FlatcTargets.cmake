if(NOT TARGET flatbuffers::flatc)
    if(CMAKE_CROSSCOMPILING)
        find_program(FLATBUFFERS_FLATC_EXECUTABLE
            NAMES flatc
            PATHS ENV PATH
            NO_DEFAULT_PATH
        )
    else()
        find_program(FLATBUFFERS_FLATC_EXECUTABLE
            NAMES flatc
            PATHS "${CMAKE_CURRENT_LIST_DIR}/../../bin/"
            NO_DEFAULT_PATH
        )
    endif()
    # TODO: In conan v2 with CMakeToolchain, can be replaced by:
    # find_program(FLATBUFFERS_FLATC_EXECUTABLE NAMES flatc)
    # # Nice enough to handle flatbuffers not in build_requires for native build
    # if(NOT FLATBUFFERS_FLATC_EXECUTABLE AND NOT CMAKE_CROSSCOMPILING)
    #     find_program(FLATBUFFERS_FLATC_EXECUTABLE
    #         NAMES flatc
    #         PATHS "${CMAKE_CURRENT_LIST_DIR}/../../bin/"
    #         NO_DEFAULT_PATH
    #     )
    # endif()

    if(FLATBUFFERS_FLATC_EXECUTABLE)
        get_filename_component(FLATBUFFERS_FLATC_EXECUTABLE "${FLATBUFFERS_FLATC_EXECUTABLE}" ABSOLUTE)
        add_executable(flatbuffers::flatc IMPORTED)
        set_property(TARGET flatbuffers::flatc PROPERTY IMPORTED_LOCATION ${FLATBUFFERS_FLATC_EXECUTABLE})
    endif()
endif()
