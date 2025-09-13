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

if(WITH_MINICORO)
    find_package(minicoro REQUIRED CONFIG)
    link_libraries(minicoro::minicoro)
endif()

if(WITH_FLATBUFFERS)
    find_package(flatbuffers REQUIRED CONFIG)
    link_libraries(flatbuffers::flatbuffers)
endif()
