# mimicking flatbuffers/all/cmake/FlatcTargets.cmake
if(NOT TARGET sbepp::sbeppc)
    if(CMAKE_CROSSCOMPILING)
        find_program(SBEPP_SBEPPC_EXECUTABLE
            NAMES sbeppc
            PATHS ENV PATH
            NO_DEFAULT_PATH
        )
    else()
        find_program(SBEPP_SBEPPC_EXECUTABLE
            NAMES sbeppc
            PATHS "${CMAKE_CURRENT_LIST_DIR}/../../bin/"
            NO_DEFAULT_PATH
        )
    endif()
    # TODO: In conan v2 with CMakeToolchain, can be replaced by:
    # find_program(SBEPP_SBEPPC_EXECUTABLE NAMES sbeppc)
    # # Nice enough to handle sbeppc not in build_requires for native build
    # if(NOT SBEPP_SBEPPC_EXECUTABLE AND NOT CMAKE_CROSSCOMPILING)
    #     find_program(SBEPP_SBEPPC_EXECUTABLE
    #         NAMES flatc
    #         PATHS "${CMAKE_CURRENT_LIST_DIR}/../../bin/"
    #         NO_DEFAULT_PATH
    #     )
    # endif()

    if(SBEPP_SBEPPC_EXECUTABLE)
        get_filename_component(
            SBEPP_SBEPPC_EXECUTABLE "${SBEPP_SBEPPC_EXECUTABLE}" ABSOLUTE)
        add_executable(sbepp::sbeppc IMPORTED)
        set_property(TARGET sbepp::sbeppc
            PROPERTY IMPORTED_LOCATION ${SBEPP_SBEPPC_EXECUTABLE})
    endif()
endif()
