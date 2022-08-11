cmake_minimum_required(VERSION 3.4)
project(libxls C)

option(WITH_CLI "Build and install cli command" OFF)

include_directories(src/include)

set(libxls_src
    src/src/endian.c
    src/src/locale.c
    src/src/ole.c
    src/src/xls.c
    src/src/xlstool.c
)

set(libxls_inc
    src/include/xls.h
)

set(libxls_inc_internal
    src/include/xls.h
    src/include/libxls/brdb.c.h
    src/include/libxls/brdb.h
    src/include/libxls/endian.h
    src/include/libxls/locale.h
    src/include/libxls/ole.h
    src/include/libxls/xlsstruct.h
    src/include/libxls/xlstool.h
    src/include/libxls/xlstypes.h
)

add_library(xlsreader ${libxls_src})
target_compile_features(xlsreader PRIVATE c_std_99)
set_target_properties(xlsreader PROPERTIES
    PUBLIC_HEADER "${libxls_inc}"
    WINDOWS_EXPORT_ALL_SYMBOLS ON
    C_EXTENSIONS ON
    C_STANDARD 99
)

if(WITH_CLI)
    add_executable(xls2csv src/src/xls2csv.c)
    target_compile_features(xls2csv PRIVATE c_std_99)
    target_link_libraries(xls2csv xlsreader)
endif()

include(GNUInstallDirs)

install(TARGETS xlsreader
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

install(FILES ${libxls_inc_internal}
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/libxls)

if(WITH_CLI)
    install(TARGETS xls2csv
        DESTINATION ${CMAKE_INSTALL_BINDIR}
    )
endif()
