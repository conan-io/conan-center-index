cmake_minimum_required(VERSION 3.1)
project(SDL2_net LANGUAGES C)

find_package(SDL2 REQUIRED CONFIG)

add_library(SDL2_net
    ${SDL_NET_SRC_DIR}/SDLnet.c
    ${SDL_NET_SRC_DIR}/SDLnetselect.c
    ${SDL_NET_SRC_DIR}/SDLnetTCP.c
    ${SDL_NET_SRC_DIR}/SDLnetUDP.c
)
target_include_directories(SDL2_net PUBLIC ${SDL_NET_SRC_DIR})
target_link_libraries(SDL2_net PUBLIC SDL2::SDL2)

if(WIN32)
    target_link_libraries(SDL2_net PRIVATE ws2_32 iphlpapi)
    target_compile_definitions(SDL2_net PRIVATE "DECLSPEC=__declspec(dllexport)")
else()
    target_compile_definitions(SDL2_net PRIVATE "DECLSPEC=__attribute__((visibility(\"default\")))")
endif()

set_target_properties(SDL2_net PROPERTIES
    PUBLIC_HEADER ${SDL_NET_SRC_DIR}/SDL_net.h
    C_VISIBILITY_PRESET hidden
)

include(GNUInstallDirs)
install(TARGETS SDL2_net
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/SDL2
)
