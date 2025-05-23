########### AGGREGATED COMPONENTS AND DEPENDENCIES FOR THE MULTI CONFIG #####################
#############################################################################################

set(aws-c-cal_COMPONENT_NAMES "")
if(DEFINED aws-c-cal_FIND_DEPENDENCY_NAMES)
  list(APPEND aws-c-cal_FIND_DEPENDENCY_NAMES aws-c-common)
  list(REMOVE_DUPLICATES aws-c-cal_FIND_DEPENDENCY_NAMES)
else()
  set(aws-c-cal_FIND_DEPENDENCY_NAMES aws-c-common)
endif()
set(aws-c-common_FIND_MODE "NO_MODULE")

########### VARIABLES #######################################################################
#############################################################################################
set(aws-c-cal_PACKAGE_FOLDER_DEBUG "C:/Users/MH.Rezaiy_110/.conan2/p/b/aws-c57fb8c4d07d80/p")
set(aws-c-cal_BUILD_MODULES_PATHS_DEBUG )


set(aws-c-cal_INCLUDE_DIRS_DEBUG "${aws-c-cal_PACKAGE_FOLDER_DEBUG}/include")
set(aws-c-cal_RES_DIRS_DEBUG )
set(aws-c-cal_DEFINITIONS_DEBUG )
set(aws-c-cal_SHARED_LINK_FLAGS_DEBUG )
set(aws-c-cal_EXE_LINK_FLAGS_DEBUG )
set(aws-c-cal_OBJECTS_DEBUG )
set(aws-c-cal_COMPILE_DEFINITIONS_DEBUG )
set(aws-c-cal_COMPILE_OPTIONS_C_DEBUG )
set(aws-c-cal_COMPILE_OPTIONS_CXX_DEBUG )
set(aws-c-cal_LIB_DIRS_DEBUG "${aws-c-cal_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-c-cal_BIN_DIRS_DEBUG )
set(aws-c-cal_LIBRARY_TYPE_DEBUG STATIC)
set(aws-c-cal_IS_HOST_WINDOWS_DEBUG 1)
set(aws-c-cal_LIBS_DEBUG aws-c-cal)
set(aws-c-cal_SYSTEM_LIBS_DEBUG ncrypt)
set(aws-c-cal_FRAMEWORK_DIRS_DEBUG )
set(aws-c-cal_FRAMEWORKS_DEBUG )
set(aws-c-cal_BUILD_DIRS_DEBUG )
set(aws-c-cal_NO_SONAME_MODE_DEBUG FALSE)


# COMPOUND VARIABLES
set(aws-c-cal_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-c-cal_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-c-cal_COMPILE_OPTIONS_C_DEBUG}>")
set(aws-c-cal_LINKER_FLAGS_DEBUG
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-c-cal_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-c-cal_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-c-cal_EXE_LINK_FLAGS_DEBUG}>")


set(aws-c-cal_COMPONENTS_DEBUG )