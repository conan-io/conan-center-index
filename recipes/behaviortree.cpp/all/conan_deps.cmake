# Inject unvendored dependencies provided by Conan

if(WITH_LEXY)
    find_package(lexy REQUIRED CONFIG)
    link_libraries(foonathan::lexy)
endif()

if(WITH_MINITRACE)
    find_package(minitrace REQUIRED CONFIG)
    link_libraries(minitrace::minitrace)
endif()

if(WITH_TINYXML2)
    find_package(tinyxml2 REQUIRED CONFIG)
    link_libraries(tinyxml2::tinyxml2)
endif()
