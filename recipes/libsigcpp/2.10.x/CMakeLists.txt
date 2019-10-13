cmake_minimum_required(VERSION 2.8.11)
project(libsigcpp CXX C)

include(${CMAKE_BINARY_DIR}/../conanbuildinfo.cmake)
conan_basic_setup()

option(LIBSIGCPP_BUILD_SHAREDLIB
       "Enable the build of the libsigcpp shared library"
       ON)

add_definitions(-DHAVE_CONFIG_H)
include( CheckIncludeFile )

if(WIN32)
    set(SHARED_LIB_EXT dll)
    if(MSVC)
        set( CMAKE_REQUIRED_INCLUDES ${CMAKE_INCLUDE_PATH} ${CMAKE_INCLUDE_PATH}/msvc )
    else(MSVC)
        set( CMAKE_REQUIRED_INCLUDES ${CMAKE_INCLUDE_PATH} ${CMAKE_INCLUDE_PATH}/mingw )
    endif(MSVC)
endif(WIN32)

set(SIGCPP_API_VERSION 2.0)
set(SICGPP_SOURCES_ROOT ${CMAKE_SOURCE_DIR}/source_subfolder)

add_definitions(-DSIGC_BUILD)

set(SICGPP_SOURCES
    ${SICGPP_SOURCES_ROOT}/sigc++/connection.cc
    ${SICGPP_SOURCES_ROOT}/sigc++/signal_base.cc
    ${SICGPP_SOURCES_ROOT}/sigc++/trackable.cc
    ${SICGPP_SOURCES_ROOT}/sigc++/adaptors/lambda/lambda.cc
    ${SICGPP_SOURCES_ROOT}/sigc++/functors/slot_base.cc)

if(LIBSIGCPP_BUILD_SHAREDLIB)
    message("LIBSIGCPP_BUILD_SHAREDLIB yes")
    add_library(sigc SHARED ${SICGPP_SOURCES})
else()
    message("LIBSIGCPP_BUILD_SHAREDLIB no")
    add_library(sigc STATIC ${SICGPP_SOURCES})
endif()

set_target_properties(sigc PROPERTIES OUTPUT_NAME sigc-${SIGCPP_API_VERSION})
target_include_directories(sigc PUBLIC ${SICGPP_SOURCES_ROOT} ${CMAKE_BINARY_DIR})

set( CMAKE_REQUIRED_LIBRARIES ${CMAKE_REQUIRED_LIBRARIES})
set( CMAKE_REQUIRED_INCLUDES ${CMAKE_REQUIRED_INCLUDES} )

check_include_file( "dlfcn.h" HAVE_DLFCN_H )
check_include_file( "inttypes.h" HAVE_INTTYPES_H )
check_include_file( "memory.h" HAVE_MEMORY_H )
check_include_file( "stdlib.h" HAVE_STDLIB_H )
check_include_file( "strings.h" HAVE_STRINGS_H )
check_include_file( "string.h" HAVE_STRING_H )
check_include_file( "sys/stat.h" HAVE_SYS_STAT_H )
check_include_file( "sys/types.h" HAVE_SYS_TYPES_H )
check_include_file( "unistd.h" HAVE_UNISTD_H )

set(STDC_HEADERS 1)
set(SIGC_HAVE_NAMESPACE_STD 1)
set(SIGC_SELF_REFERENCE_IN_MEMBER_INITIALIZATION 1)

if(MSVC)
    SET(SIGC_MSVC_TEMPLATE_SPECIALIZATION_OPERATOR_OVERLOAD 1)
    SET(SIGC_NEW_DELETE_IN_LIBRARY_ONLY 1)
endif()

if(CMAKE_COMPILER_IS_GNUCXX)
SET(SIGC_GCC_TEMPLATE_SPECIALIZATION_OPERATOR_OVERLOAD 1)
endif()

configure_file( ${CMAKE_CURRENT_SOURCE_DIR}/config.h.cmake ${CMAKE_CURRENT_BINARY_DIR}/config.h )
configure_file( ${CMAKE_CURRENT_SOURCE_DIR}/config.h.cmake ${CMAKE_CURRENT_BINARY_DIR}/sigc++/config.h )
configure_file( ${CMAKE_CURRENT_SOURCE_DIR}/sigc++config.h.cmake ${CMAKE_CURRENT_BINARY_DIR}/sigc++config.h )
configure_file( ${CMAKE_CURRENT_SOURCE_DIR}/sigc++config.h.cmake ${CMAKE_CURRENT_BINARY_DIR}/sigc++/sigc++config.h )

install(TARGETS sigc
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/sigc++config.h DESTINATION include)
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/sigc++/sigc++config.h DESTINATION include/sigc++)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/sigc++.h DESTINATION include/sigc++)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/bind.h DESTINATION include/sigc++)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/bind_return.h DESTINATION include/sigc++)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/connection.h DESTINATION include/sigc++)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/limit_reference.h DESTINATION include/sigc++)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/reference_wrapper.h DESTINATION include/sigc++)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/retype_return.h DESTINATION include/sigc++)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/signal.h DESTINATION include/sigc++)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/signal_base.h DESTINATION include/sigc++)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/slot.h DESTINATION include/sigc++)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/trackable.h DESTINATION include/sigc++)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/type_traits.h DESTINATION include/sigc++)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/visit_each.h DESTINATION include/sigc++)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/adaptors/adaptors.h DESTINATION include/sigc++/adaptors)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/adaptors/adaptor_trait.h DESTINATION include/sigc++/adaptors)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/adaptors/bind.h DESTINATION include/sigc++/adaptors)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/adaptors/bind_return.h DESTINATION include/sigc++/adaptors)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/adaptors/bound_argument.h DESTINATION include/sigc++/adaptors)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/adaptors/compose.h DESTINATION include/sigc++/adaptors)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/adaptors/deduce_result_type.h DESTINATION include/sigc++/adaptors)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/adaptors/exception_catch.h DESTINATION include/sigc++/adaptors)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/adaptors/hide.h DESTINATION include/sigc++/adaptors)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/adaptors/retype.h DESTINATION include/sigc++/adaptors)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/adaptors/retype_return.h DESTINATION include/sigc++/adaptors)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/adaptors/track_obj.h DESTINATION include/sigc++/adaptors)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/adaptors/lambda/base.h DESTINATION include/sigc++/adaptors/lambda)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/adaptors/lambda/select.h DESTINATION include/sigc++/adaptors/lambda)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/functors/functors.h DESTINATION include/sigc++/functors)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/functors/functor_trait.h DESTINATION include/sigc++/functors)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/functors/mem_fun.h DESTINATION include/sigc++/functors)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/functors/ptr_fun.h DESTINATION include/sigc++/functors)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/functors/slot.h DESTINATION include/sigc++/functors)
install(FILES ${SICGPP_SOURCES_ROOT}/sigc++/functors/slot_base.h DESTINATION include/sigc++/functors)


