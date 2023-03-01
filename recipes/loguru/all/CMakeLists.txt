cmake_minimum_required(VERSION 3.8)
project(loguru LANGUAGES CXX)

include(GNUInstallDirs)

option(LOGURU_USE_FMTLIB "Use fmtlib project to format text")

option(LOGURU_SCOPE_TEXT_SIZE "Maximum length of text that can be printed by a LOG_SCOPE.")
option(LOGURU_FILENAME_WIDTH "Width of the column containing the file name")
option(LOGURU_THREADNAME_WIDTH "Width of the column containing the thread name")
option(LOGURU_SCOPE_TIME_PRECISION "Resolution of scope timers: 3=ms, 6=us, 9=ns")

option(LOGURU_CATCH_SIGABRT "Should Loguru catch SIGABRT to print stack trace etc?")
option(LOGURU_VERBOSE_SCOPE_ENDINGS "Show milliseconds and scope name at end of scope")
option(LOGURU_REDEFINE_ASSERT "Redefine default c++ assert value")
option(LOGURU_WITH_STREAMS "Extends loguru to enable std::stream-style logging")
option(LOGURU_WITH_FILEABS "Check of file change will be performed on every call to file_log")
option(LOGURU_RTTI "Support to runtime type information")
option(LOGURU_REPLACE_GLOG "Make Loguru mimic GLOG as close as possible")


if (LOGURU_USE_FMTLIB)
    find_package(fmt CONFIG REQUIRED)
endif()


add_library(${PROJECT_NAME} ${LOGURU_SRC_DIR}/loguru.cpp ${LOGURU_SRC_DIR}/loguru.hpp)
target_link_libraries(${PROJECT_NAME} PUBLIC $<$<BOOL:${LOGURU_USE_FMTLIB}>:fmt::fmt>)
set_target_properties(${PROJECT_NAME} PROPERTIES
    WINDOWS_EXPORT_ALL_SYMBOLS ON
    PUBLIC_HEADER "${LOGURU_SRC_DIR}/loguru.hpp"
)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
target_compile_definitions(${PROJECT_NAME} PRIVATE
    LOGURU_SCOPE_TEXT_SIZE=${LOGURU_SCOPE_TEXT_SIZE}
    LOGURU_FILENAME_WIDTH=${LOGURU_FILENAME_WIDTH}
    LOGURU_THREADNAME_WIDTH=${LOGURU_THREADNAME_WIDTH}
    LOGURU_SCOPE_TIME_PRECISION=${LOGURU_SCOPE_TIME_PRECISION}
    LOGURU_CATCH_SIGABRT=${LOGURU_CATCH_SIGABRT}
    LOGURU_VERBOSE_SCOPE_ENDINGS=${LOGURU_VERBOSE_SCOPE_ENDINGS}
    LOGURU_REDEFINE_ASSERT=${LOGURU_REDEFINE_ASSERT}
    LOGURU_WITH_STREAMS=${LOGURU_WITH_STREAMS}
    LOGURU_WITH_FILEABS=${LOGURU_WITH_FILEABS}
    LOGURU_RTTI=${LOGURU_RTTI}
    LOGURU_REPLACE_GLOG=${LOGURU_REPLACE_GLOG}
)

install(
    TARGETS ${PROJECT_NAME}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
