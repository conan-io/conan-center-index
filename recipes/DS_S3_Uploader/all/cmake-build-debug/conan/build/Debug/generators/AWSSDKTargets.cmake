# Load the debug and release variables
file(GLOB DATA_FILES "${CMAKE_CURRENT_LIST_DIR}/AWSSDK-*-data.cmake")

foreach(f ${DATA_FILES})
    include(${f})
endforeach()

# Create the targets for all the components
foreach(_COMPONENT ${aws-sdk-cpp_COMPONENT_NAMES} )
    if(NOT TARGET ${_COMPONENT})
        add_library(${_COMPONENT} INTERFACE IMPORTED)
        message(${AWSSDK_MESSAGE_MODE} "Conan: Component target declared '${_COMPONENT}'")
    endif()
endforeach()

if(NOT TARGET aws-sdk-cpp::aws-sdk-cpp)
    add_library(aws-sdk-cpp::aws-sdk-cpp INTERFACE IMPORTED)
    message(${AWSSDK_MESSAGE_MODE} "Conan: Target declared 'aws-sdk-cpp::aws-sdk-cpp'")
endif()
# Load the debug and release library finders
file(GLOB CONFIG_FILES "${CMAKE_CURRENT_LIST_DIR}/AWSSDK-Target-*.cmake")

foreach(f ${CONFIG_FILES})
    include(${f})
endforeach()