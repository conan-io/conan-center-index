########### AGGREGATED COMPONENTS AND DEPENDENCIES FOR THE MULTI CONFIG #####################
#############################################################################################

set(aws-c-common_COMPONENT_NAMES "")
if(DEFINED aws-c-common_FIND_DEPENDENCY_NAMES)
  list(APPEND aws-c-common_FIND_DEPENDENCY_NAMES )
  list(REMOVE_DUPLICATES aws-c-common_FIND_DEPENDENCY_NAMES)
else()
  set(aws-c-common_FIND_DEPENDENCY_NAMES )
endif()

########### VARIABLES #######################################################################
#############################################################################################
set(aws-c-common_PACKAGE_FOLDER_DEBUG "C:/Users/MH.Rezaiy_110/.conan2/p/b/aws-c10d8203b7fc81/p")
set(aws-c-common_BUILD_MODULES_PATHS_DEBUG )


set(aws-c-common_INCLUDE_DIRS_DEBUG "${aws-c-common_PACKAGE_FOLDER_DEBUG}/include")
set(aws-c-common_RES_DIRS_DEBUG )
set(aws-c-common_DEFINITIONS_DEBUG )
set(aws-c-common_SHARED_LINK_FLAGS_DEBUG )
set(aws-c-common_EXE_LINK_FLAGS_DEBUG )
set(aws-c-common_OBJECTS_DEBUG )
set(aws-c-common_COMPILE_DEFINITIONS_DEBUG )
set(aws-c-common_COMPILE_OPTIONS_C_DEBUG )
set(aws-c-common_COMPILE_OPTIONS_CXX_DEBUG )
set(aws-c-common_LIB_DIRS_DEBUG "${aws-c-common_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-c-common_BIN_DIRS_DEBUG )
set(aws-c-common_LIBRARY_TYPE_DEBUG STATIC)
set(aws-c-common_IS_HOST_WINDOWS_DEBUG 1)
set(aws-c-common_LIBS_DEBUG aws-c-common)
set(aws-c-common_SYSTEM_LIBS_DEBUG bcrypt ws2_32 kernel32 shlwapi psapi)
set(aws-c-common_FRAMEWORK_DIRS_DEBUG )
set(aws-c-common_FRAMEWORKS_DEBUG )
set(aws-c-common_BUILD_DIRS_DEBUG "${aws-c-common_PACKAGE_FOLDER_DEBUG}/lib/cmake")
set(aws-c-common_NO_SONAME_MODE_DEBUG FALSE)


# COMPOUND VARIABLES
set(aws-c-common_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-c-common_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-c-common_COMPILE_OPTIONS_C_DEBUG}>")
set(aws-c-common_LINKER_FLAGS_DEBUG
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-c-common_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-c-common_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-c-common_EXE_LINK_FLAGS_DEBUG}>")


set(aws-c-common_COMPONENTS_DEBUG )