cmake_minimum_required(VERSION 3.25)
project(loguru)

set(CMAKE_CXX_STANDARD 11)
set(src loguru.cpp loguru.hpp)

if (LOGURU_STATIC)
    message("-- loguru: building a static library")
    add_library(loguru STATIC ${src})
else ()
    message("-- loguru: building a shared library")
    add_library(loguru SHARED ${src})
endif ()

if (LOGURU_USE_FMTLIB)
    message("-- loguru: using fmtlib")
    target_compile_definitions(loguru PUBLIC -DLOGURU_USE_FMTLIB)
    find_package(fmt CONFIG REQUIRED)
    target_link_libraries(loguru PUBLIC fmt::fmt)
endif ()

if (LOGURU_SCOPE_TEXT_SIZE)
    message("-- loguru: setting LOGURU_SCOPE_TEXT_SIZE=${LOGURU_SCOPE_TEXT_SIZE}")
    target_compile_definitions(loguru PUBLIC -DLOGURU_SCOPE_TEXT_SIZE=${LOGURU_SCOPE_TEXT_SIZE})
endif ()

if (LOGURU_FILENAME_WIDTH)
    message("-- loguru: setting LOGURU_FILENAME_WIDTH=${LOGURU_FILENAME_WIDTH}")
    target_compile_definitions(loguru PUBLIC -DLOGURU_FILENAME_WIDTH=${LOGURU_FILENAME_WIDTH})
endif ()

if (LOGURU_THREADNAME_WIDTH)
    message("-- loguru: setting LOGURU_THREADNAME_WIDTH=${LOGURU_THREADNAME_WIDTH}")
    target_compile_definitions(loguru PUBLIC -DLOGURU_THREADNAME_WIDTH=${LOGURU_THREADNAME_WIDTH})
endif ()

if (LOGURU_SCOPE_TIME_PRECISION)
    message("-- loguru: setting LOGURU_SCOPE_TIME_PRECISION=${LOGURU_SCOPE_TIME_PRECISION}")
    target_compile_definitions(loguru PUBLIC -DLOGURU_SCOPE_TIME_PRECISION=${LOGURU_SCOPE_TIME_PRECISION})
endif ()

message("-- loguru: setting LOGURU_CATCH_SIGABRT=${LOGURU_CATCH_SIGABRT}")
target_compile_definitions(loguru PUBLIC -DLOGURU_CATCH_SIGABRT=${LOGURU_CATCH_SIGABRT})

message("-- loguru: setting LOGURU_VERBOSE_SCOPE_ENDINGS=${LOGURU_VERBOSE_SCOPE_ENDINGS}")
target_compile_definitions(loguru PUBLIC -DLOGURU_VERBOSE_SCOPE_ENDINGS=${LOGURU_VERBOSE_SCOPE_ENDINGS})

message("-- loguru: setting LOGURU_REDEFINE_ASSERT=${LOGURU_REDEFINE_ASSERT}")
target_compile_definitions(loguru PUBLIC -DLOGURU_REDEFINE_ASSERT=${LOGURU_REDEFINE_ASSERT})

message("-- loguru: setting LOGURU_WITH_STREAMS=${LOGURU_WITH_STREAMS}")
target_compile_definitions(loguru PUBLIC -DLOGURU_WITH_STREAMS=${LOGURU_WITH_STREAMS})

message("-- loguru: setting LOGURU_WITH_FILEABS=${LOGURU_WITH_FILEABS}")
target_compile_definitions(loguru PUBLIC -DLOGURU_WITH_FILEABS=${LOGURU_WITH_FILEABS})

message("-- loguru: setting LOGURU_WITH_RTTI=${LOGURU_WITH_RTTI}")
target_compile_definitions(loguru PUBLIC -DLOGURU_WITH_RTTI=${LOGURU_WITH_RTTI})

message("-- loguru: setting LOGURU_REPLACE_GLOG=${LOGURU_REPLACE_GLOG}")
target_compile_definitions(loguru PUBLIC -DLOGURU_REPLACE_GLOG=${LOGURU_REPLACE_GLOG})

install(TARGETS loguru)
