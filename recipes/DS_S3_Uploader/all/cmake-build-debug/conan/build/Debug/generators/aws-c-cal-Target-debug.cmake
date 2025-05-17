# Avoid multiple calls to find_package to append duplicated properties to the targets
include_guard()########### VARIABLES #######################################################################
#############################################################################################
set(aws-c-cal_FRAMEWORKS_FOUND_DEBUG "") # Will be filled later
conan_find_apple_frameworks(aws-c-cal_FRAMEWORKS_FOUND_DEBUG "${aws-c-cal_FRAMEWORKS_DEBUG}" "${aws-c-cal_FRAMEWORK_DIRS_DEBUG}")

set(aws-c-cal_LIBRARIES_TARGETS "") # Will be filled later


######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
if(NOT TARGET aws-c-cal_DEPS_TARGET)
    add_library(aws-c-cal_DEPS_TARGET INTERFACE IMPORTED)
endif()

set_property(TARGET aws-c-cal_DEPS_TARGET
             APPEND PROPERTY INTERFACE_LINK_LIBRARIES
             $<$<CONFIG:Debug>:${aws-c-cal_FRAMEWORKS_FOUND_DEBUG}>
             $<$<CONFIG:Debug>:${aws-c-cal_SYSTEM_LIBS_DEBUG}>
             $<$<CONFIG:Debug>:AWS::aws-c-common>)

####### Find the libraries declared in cpp_info.libs, create an IMPORTED target for each one and link the
####### aws-c-cal_DEPS_TARGET to all of them
conan_package_library_targets("${aws-c-cal_LIBS_DEBUG}"    # libraries
                              "${aws-c-cal_LIB_DIRS_DEBUG}" # package_libdir
                              "${aws-c-cal_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-c-cal_LIBRARY_TYPE_DEBUG}"
                              "${aws-c-cal_IS_HOST_WINDOWS_DEBUG}"
                              aws-c-cal_DEPS_TARGET
                              aws-c-cal_LIBRARIES_TARGETS  # out_libraries_targets
                              "_DEBUG"
                              "aws-c-cal"    # package_name
                              "${aws-c-cal_NO_SONAME_MODE_DEBUG}")  # soname

# FIXME: What is the result of this for multi-config? All configs adding themselves to path?
set(CMAKE_MODULE_PATH ${aws-c-cal_BUILD_DIRS_DEBUG} ${CMAKE_MODULE_PATH})

########## GLOBAL TARGET PROPERTIES Debug ########################################
    set_property(TARGET AWS::aws-c-cal
                 APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                 $<$<CONFIG:Debug>:${aws-c-cal_OBJECTS_DEBUG}>
                 $<$<CONFIG:Debug>:${aws-c-cal_LIBRARIES_TARGETS}>
                 )

    if("${aws-c-cal_LIBS_DEBUG}" STREQUAL "")
        # If the package is not declaring any "cpp_info.libs" the package deps, system libs,
        # frameworks etc are not linked to the imported targets and we need to do it to the
        # global target
        set_property(TARGET AWS::aws-c-cal
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     aws-c-cal_DEPS_TARGET)
    endif()

    set_property(TARGET AWS::aws-c-cal
                 APPEND PROPERTY INTERFACE_LINK_OPTIONS
                 $<$<CONFIG:Debug>:${aws-c-cal_LINKER_FLAGS_DEBUG}>)
    set_property(TARGET AWS::aws-c-cal
                 APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                 $<$<CONFIG:Debug>:${aws-c-cal_INCLUDE_DIRS_DEBUG}>)
    # Necessary to find LINK shared libraries in Linux
    set_property(TARGET AWS::aws-c-cal
                 APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                 $<$<CONFIG:Debug>:${aws-c-cal_LIB_DIRS_DEBUG}>)
    set_property(TARGET AWS::aws-c-cal
                 APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                 $<$<CONFIG:Debug>:${aws-c-cal_COMPILE_DEFINITIONS_DEBUG}>)
    set_property(TARGET AWS::aws-c-cal
                 APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                 $<$<CONFIG:Debug>:${aws-c-cal_COMPILE_OPTIONS_DEBUG}>)

########## For the modules (FindXXX)
set(aws-c-cal_LIBRARIES_DEBUG AWS::aws-c-cal)
