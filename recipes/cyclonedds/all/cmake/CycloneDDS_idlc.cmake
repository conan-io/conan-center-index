if(NOT TARGET CycloneDDS::idlc)
    if(CMAKE_CROSSCOMPILING)
        find_program(CYCLONEDDS_IDLC_EXECUTABLE
            NAMES idlc
            PATHS ENV PATH
            NO_DEFAULT_PATH
        )
    else()
        find_program(CYCLONEDDS_IDLC_EXECUTABLE
            NAMES idlc
            PATHS "${CMAKE_CURRENT_LIST_DIR}/../../bin/"
            NO_DEFAULT_PATH
        )
    endif()
    # TODO: In conan v2 with CMakeToolchain, can be replaced by:
    # find_program(CYCLONEDDS_IDLC_EXECUTABLE NAMES idlc)
    # # Nice enough to handle CycloneDDS not in build_requires for native build
    # if(NOT CYCLONEDDS_IDLC_EXECUTABLE AND NOT CMAKE_CROSSCOMPILING)
    #     find_program(CYCLONEDDS_IDLC_EXECUTABLE
    #         NAMES idlc
    #         PATHS "${CMAKE_CURRENT_LIST_DIR}/../../bin/"
    #         NO_DEFAULT_PATH
    #     )
    # endif()

    if(CYCLONEDDS_IDLC_EXECUTABLE)
        get_filename_component(CYCLONEDDS_IDLC_EXECUTABLE "${CYCLONEDDS_IDLC_EXECUTABLE}" ABSOLUTE)
        add_executable(CycloneDDS::idlc IMPORTED)
        set_property(TARGET CycloneDDS::idlc PROPERTY IMPORTED_LOCATION ${CYCLONEDDS_IDLC_EXECUTABLE})
    endif()
endif()
