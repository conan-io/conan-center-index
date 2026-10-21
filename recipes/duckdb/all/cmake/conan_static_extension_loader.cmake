# Conan: since 2.0.0 DuckDB registers its statically linked extensions and capabilities through a loader that upstream
# generates into each program (extension/loader). Build that loader once into a library instead; consumers force-link
# it through the anchor symbol in conan_static_extension_loader.cpp (see the recipe's package_info()).
add_library(duckdb_static_extension_loader STATIC "${CMAKE_CURRENT_LIST_DIR}/conan_static_extension_loader.cpp")
target_include_directories(duckdb_static_extension_loader PRIVATE "${PROJECT_SOURCE_DIR}/src/include")
# EXPLICIT: only generate duckdb_register_static_extensions(); the .cpp above calls it before main
duckdb_link_extensions(duckdb_static_extension_loader PRIVATE EXPLICIT
                       ${DUCKDB_STATICALLY_LINKED_CAPABILITIES} ${DUCKDB_STATICALLY_LINKED_EXTENSIONS})
install(TARGETS duckdb_static_extension_loader
        LIBRARY DESTINATION "${INSTALL_LIB_DIR}"
        ARCHIVE DESTINATION "${INSTALL_LIB_DIR}")
