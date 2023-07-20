cmake_minimum_required(VERSION 3.4)
project(microprofile)

option(MICROPROFILE_USE_CONFIG_FILE "Use user provided configuration in microprofile.config.h file." ON)

set(MICROPROFILE_EXPORT_FILENAME microprofile.export.h)
set(MICROPROFILE_CONFIG_HEADER ${PROJECT_SOURCE_DIR}/microprofile.config.h)
set(MICROPROFILE_PUBLIC_HEADERS
        ${PROJECT_SOURCE_DIR}/microprofile.h
        ${CMAKE_CURRENT_BINARY_DIR}/${MICROPROFILE_EXPORT_FILENAME}
)

set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

add_library(${PROJECT_NAME} microprofile.h microprofile.cpp)

include(GenerateExportHeader)
generate_export_header(${PROJECT_NAME}
        EXPORT_MACRO_NAME MICROPROFILE_API
        EXPORT_FILE_NAME ${MICROPROFILE_EXPORT_FILENAME}
)

target_include_directories(${PROJECT_NAME} PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>
        $<INSTALL_INTERFACE:include>
)

if (MICROPROFILE_USE_CONFIG_FILE)
    target_compile_definitions(${PROJECT_NAME} PUBLIC MICROPROFILE_USE_CONFIG)
endif()

target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_11)

target_link_libraries(${PROJECT_NAME} PRIVATE Threads::Threads)

if (WIN32)
    target_link_libraries(${PROJECT_NAME} PRIVATE ws2_32)
endif()

if (MP_MINIZ)
    find_package(miniz REQUIRED CONFIG)
    target_link_libraries(${PROJECT_NAME} PRIVATE miniz::miniz)
endif()

if (MP_GPU_TIMERS_VULKAN)
    find_package(Vulkan REQUIRED)
    target_link_libraries(${PROJECT_NAME} PRIVATE Vulkan::Vulkan)
endif()

set_target_properties(${PROJECT_NAME} PROPERTIES PUBLIC_HEADER "${MICROPROFILE_PUBLIC_HEADERS}")

include(GNUInstallDirs)
install(TARGETS ${PROJECT_NAME}
        PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${PROJECT_NAME}
)
if (MICROPROFILE_USE_CONFIG_FILE)
    install(FILES ${MICROPROFILE_CONFIG_HEADER}
            DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${PROJECT_NAME}
            PERMISSIONS OWNER_WRITE OWNER_READ GROUP_READ WORLD_READ
    )
endif()
