cmake_minimum_required(VERSION 3.8)
project(alac LANGUAGES C CXX)

include(GNUInstallDirs)

file(GLOB ALAC_LIB_SRCS src/codec/*.c src/codec/*.cpp)
file(GLOB ALAC_LIB_PUBLIC_HDRS src/codec/ALAC*.h)

add_library(alac ${ALAC_LIB_SRCS})
target_include_directories(alac PUBLIC src/codec)
set_property(TARGET alac PROPERTY WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
target_compile_definitions(alac
    PRIVATE
        $<IF:$<BOOL:${APPLE}>,TARGET_OS_MAC=1,TARGET_OS_MAC=0>
)

install(FILES ${ALAC_LIB_PUBLIC_HDRS} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(TARGETS alac
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})

if(ALAC_BUILD_UTILITY)
    file(GLOB ALAC_CONVERTER_SRCS src/convert-utility/*.cpp)

    add_executable(alacconvert ${ALAC_CONVERTER_SRCS})
    target_link_libraries(alacconvert PRIVATE alac)
    target_compile_definitions(alacconvert
        PRIVATE
            $<IF:$<PLATFORM_ID:Windows>,TARGET_OS_WIN32=1,TARGET_OS_WIN32=0>
    )

    install(TARGETS alacconvert DESTINATION ${CMAKE_INSTALL_BINDIR})
endif()
