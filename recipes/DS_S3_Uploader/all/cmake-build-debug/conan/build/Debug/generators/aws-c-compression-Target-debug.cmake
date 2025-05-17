# Avoid multiple calls to find_package to append duplicated properties to the targets
include_guard()########### VARIABLES #######################################################################
#############################################################################################
set(aws-c-compression_FRAMEWORKS_FOUND_DEBUG "") # Will be filled later
conan_find_apple_frameworks(aws-c-compression_FRAMEWORKS_FOUND_DEBUG "${aws-c-compression_FRAMEWORKS_DEBUG}" "${aws-c-compression_FRAMEWORK_DIRS_DEBUG}")

set(aws-c-compression_LIBRARIES_TARGETS "") # Will be filled later


######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
if(NOT TARGET aws-c-compression_DEPS_TARGET)
    add_library(aws-c-compression_DEPS_TARGET INTERFACE IMPORTED)
endif()

set_property(TARGET aws-c-compression_DEPS_TARGET
             APPEND PROPERTY INTERFACE_LINK_LIBRARIES
             $<$<CONFIG:Debug>:${aws-c-compression_FRAMEWORKS_FOUND_DEBUG}>
             $<$<CONFIG:Debug>:${aws-c-compression_SYSTEM_LIBS_DEBUG}>
             $<$<CONFIG:Debug>:AWS::aws-c-common>)

####### Find the libraries declared in cpp_info.libs, create an IMPORTED target for each one and link the
####### aws-c-compression_DEPS_TARGET to all of them
conan_package_library_targets("${aws-c-compression_LIBS_DEBUG}"    # libraries
                              "${aws-c-compression_LIB_DIRS_DEBUG}" # package_libdir
                              "${aws-c-compression_BIN_DIRS_DEBUG}" # package_bindir
                              "${aws-c-compression_LIBRARY_TYPE_DEBUG}"
                              "${aws-c-compression_IS_HOST_WINDOWS_DEBUG}"
                              aws-c-compression_DEPS_TARGET
                              aws-c-compression_LIBRARIES_TARGETS  # out_libraries_targets
                              "_DEBUG"
                              "aws-c-compression"    # package_name
                              "${aws-c-compression_NO_SONAME_MODE_DEBUG}")  # soname

# FIXME: What is the result of this for multi-config? All configs adding themselves to path?
set(CMAKE_MODULE_PATH ${aws-c-compression_BUILD_DIRS_DEBUG} ${CMAKE_MODULE_PATH})

########## GLOBAL TARGET PROPERTIES Debug ########################################
    set_property(TARGET AWS::aws-c-compression
                 APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                 $<$<CONFIG:Debug>:${aws-c-compression_OBJECTS_DEBUG}>
                 $<$<CONFIG:Debug>:${aws-c-compression_LIBRARIES_TARGETS}>
                 )

    if("${aws-c-compression_LIBS_DEBUG}" STREQUAL "")
        # If the package is not declaring any "cpp_info.libs" the package deps, system libs,
        # frameworks etc are not linked to the imported targets and we need to do it to the
        # global target
        set_property(TARGET AWS::aws-c-compression
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     aws-c-compression_DEPS_TARGET)
    endif()

    set_property(TARGET AWS::aws-c-compression
                 APPEND PROPERTY INTERFACE_LINK_OPTIONS
                 $<$<CONFIG:Debug>:${aws-c-compression_LINKER_FLAGS_DEBUG}>)
    set_property(TARGET AWS::aws-c-compression
                 APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                 $<$<CONFIG:Debug>:${aws-c-compression_INCLUDE_DIRS_DEBUG}>)
    # Necessary to find LINK shared libraries in Linux
    set_property(TARGET AWS::aws-c-compression
                 APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                 $<$<CONFIG:Debug>:${aws-c-compression_LIB_DIRS_DEBUG}>)
    set_property(TARGET AWS::aws-c-compression
                 APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                 $<$<CONFIG:Debug>:${aws-c-compression_COMPILE_DEFINITIONS_DEBUG}>)
    set_property(TARGET AWS::aws-c-compression
                 APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                 $<$<CONFIG:Debug>:${aws-c-compression_COMPILE_OPTIONS_DEBUG}>)

########## For the modules (FindXXX)
set(aws-c-compression_LIBRARIES_DEBUG AWS::aws-c-compression)
