# Load the debug and release variables
file(GLOB DATA_FILES "${CMAKE_CURRENT_LIST_DIR}/aws-crt-cpp-*-data.cmake")

foreach(f ${DATA_FILES})
    include(${f})
endforeach()

# Create the targets for all the components
foreach(_COMPONENT ${aws-crt-cpp_COMPONENT_NAMES} )
    if(NOT TARGET ${_COMPONENT})
        add_library(${_COMPONENT} INTERFACE IMPORTED)
        message(${aws-crt-cpp_MESSAGE_MODE} "Conan: Component target declared '${_COMPONENT}'")
    endif()
endforeach()

if(NOT TARGET AWS::aws-crt-cpp)
    add_library(AWS::aws-crt-cpp INTERFACE IMPORTED)
    message(${aws-crt-cpp_MESSAGE_MODE} "Conan: Target declared 'AWS::aws-crt-cpp'")
endif()
# Load the debug and release library finders
file(GLOB CONFIG_FILES "${CMAKE_CURRENT_LIST_DIR}/aws-crt-cpp-Target-*.cmake")

foreach(f ${CONFIG_FILES})
    include(${f})
endforeach()