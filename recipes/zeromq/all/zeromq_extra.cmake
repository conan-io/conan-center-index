# This script should only run when included in a FindXXX.cmake module
if(NOT ZeroMQ_LIB_DIRS)
    return()
endif()

if(NOT TARGET libzmq)
    add_library(libzmq INTERFACE IMPORTED)
    set_property(TARGET libzmq PROPERTY INTERFACE_LINK_LIBRARIES ZeroMQ::ZeroMQ)
endif()
if(NOT TARGET libzmq-static)
    add_library(libzmq-static INTERFACE IMPORTED)
    set_property(TARGET libzmq-static PROPERTY INTERFACE_LINK_LIBRARIES ZeroMQ::ZeroMQ)
endif()
