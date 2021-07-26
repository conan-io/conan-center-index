if(NOT TARGET gRPC::grpc_cpp_plugin)
    if(CMAKE_CROSSCOMPILING)
        find_program(GRPC_CPP_PLUGIN_PROGRAM 
            NAMES grpc_cpp_plugin 
            PATHS ENV 
            PATH NO_DEFAULT_PATH)
    else()
        find_program(GRPC_CPP_PLUGIN_PROGRAM 
            NAMES grpc_cpp_plugin 
            PATHS "${CMAKE_CURRENT_LIST_DIR}/../../bin/"
            NO_DEFAULT_PATH)
    endif()

    get_filename_component(GRPC_CPP_PLUGIN_PROGRAM "${GRPC_CPP_PLUGIN_PROGRAM}" ABSOLUTE)

    add_executable(gRPC::grpc_cpp_plugin IMPORTED)
    set_property(TARGET gRPC::grpc_cpp_plugin PROPERTY IMPORTED_LOCATION ${GRPC_CPP_PLUGIN_PROGRAM})
endif()
