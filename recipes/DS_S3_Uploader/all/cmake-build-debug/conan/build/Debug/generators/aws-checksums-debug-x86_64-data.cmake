########### AGGREGATED COMPONENTS AND DEPENDENCIES FOR THE MULTI CONFIG #####################
#############################################################################################

set(aws-checksums_COMPONENT_NAMES "")
if(DEFINED aws-checksums_FIND_DEPENDENCY_NAMES)
  list(APPEND aws-checksums_FIND_DEPENDENCY_NAMES aws-c-common)
  list(REMOVE_DUPLICATES aws-checksums_FIND_DEPENDENCY_NAMES)
else()
  set(aws-checksums_FIND_DEPENDENCY_NAMES aws-c-common)
endif()
set(aws-c-common_FIND_MODE "NO_MODULE")

########### VARIABLES #######################################################################
#############################################################################################
set(aws-checksums_PACKAGE_FOLDER_DEBUG "C:/Users/MH.Rezaiy_110/.conan2/p/b/aws-c4d72a491e51b9/p")
set(aws-checksums_BUILD_MODULES_PATHS_DEBUG )


set(aws-checksums_INCLUDE_DIRS_DEBUG "${aws-checksums_PACKAGE_FOLDER_DEBUG}/include")
set(aws-checksums_RES_DIRS_DEBUG )
set(aws-checksums_DEFINITIONS_DEBUG )
set(aws-checksums_SHARED_LINK_FLAGS_DEBUG )
set(aws-checksums_EXE_LINK_FLAGS_DEBUG )
set(aws-checksums_OBJECTS_DEBUG )
set(aws-checksums_COMPILE_DEFINITIONS_DEBUG )
set(aws-checksums_COMPILE_OPTIONS_C_DEBUG )
set(aws-checksums_COMPILE_OPTIONS_CXX_DEBUG )
set(aws-checksums_LIB_DIRS_DEBUG "${aws-checksums_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-checksums_BIN_DIRS_DEBUG )
set(aws-checksums_LIBRARY_TYPE_DEBUG STATIC)
set(aws-checksums_IS_HOST_WINDOWS_DEBUG 1)
set(aws-checksums_LIBS_DEBUG aws-checksums)
set(aws-checksums_SYSTEM_LIBS_DEBUG )
set(aws-checksums_FRAMEWORK_DIRS_DEBUG )
set(aws-checksums_FRAMEWORKS_DEBUG )
set(aws-checksums_BUILD_DIRS_DEBUG )
set(aws-checksums_NO_SONAME_MODE_DEBUG FALSE)


# COMPOUND VARIABLES
set(aws-checksums_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-checksums_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-checksums_COMPILE_OPTIONS_C_DEBUG}>")
set(aws-checksums_LINKER_FLAGS_DEBUG
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-checksums_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-checksums_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-checksums_EXE_LINK_FLAGS_DEBUG}>")


set(aws-checksums_COMPONENTS_DEBUG )