########## MACROS ###########################################################################
#############################################################################################

# Requires CMake > 3.15
if(${CMAKE_VERSION} VERSION_LESS "3.15")
    message(FATAL_ERROR "The 'CMakeDeps' generator only works with CMake >= 3.15")
endif()

if(aws-c-cal_FIND_QUIETLY)
    set(aws-c-cal_MESSAGE_MODE VERBOSE)
else()
    set(aws-c-cal_MESSAGE_MODE STATUS)
endif()

include(${CMAKE_CURRENT_LIST_DIR}/cmakedeps_macros.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/aws-c-calTargets.cmake)
include(CMakeFindDependencyMacro)

check_build_type_defined()

foreach(_DEPENDENCY ${aws-c-cal_FIND_DEPENDENCY_NAMES} )
    # Check that we have not already called a find_package with the transitive dependency
    if(NOT ${_DEPENDENCY}_FOUND)
        find_dependency(${_DEPENDENCY} REQUIRED ${${_DEPENDENCY}_FIND_MODE})
    endif()
endforeach()

set(aws-c-cal_VERSION_STRING "0.6.14")
set(aws-c-cal_INCLUDE_DIRS ${aws-c-cal_INCLUDE_DIRS_DEBUG} )
set(aws-c-cal_INCLUDE_DIR ${aws-c-cal_INCLUDE_DIRS_DEBUG} )
set(aws-c-cal_LIBRARIES ${aws-c-cal_LIBRARIES_DEBUG} )
set(aws-c-cal_DEFINITIONS ${aws-c-cal_DEFINITIONS_DEBUG} )


# Only the last installed configuration BUILD_MODULES are included to avoid the collision
foreach(_BUILD_MODULE ${aws-c-cal_BUILD_MODULES_PATHS_DEBUG} )
    message(${aws-c-cal_MESSAGE_MODE} "Conan: Including build module from '${_BUILD_MODULE}'")
    include(${_BUILD_MODULE})
endforeach()


