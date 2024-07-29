cmake_minimum_required(VERSION 3.15)
project(libid3tag LANGUAGES C)

file(GLOB SOURCES "*.c" "*.h")
add_library(libid3tag ${SOURCES} ${HEADERS})
target_include_directories(libid3tag PRIVATE msvc++)

# https://github.com/markjeee/libid3tag/blob/master/msvc%2B%2B/libid3tag.dsp#L43-L44
target_compile_options(libid3tag PRIVATE /W2 "$<$<CONFIG:Debug>:/Od;/GZ>" "$<$<CONFIG:Release>:/O2>")
target_compile_definitions(libid3tag PRIVATE HAVE_CONFIG_H "$<$<CONFIG:Debug>:DEBUG;>" "$<$<CONFIG:Release>:NDEBUG>")
set_property(TARGET libid3tag PROPERTY WINDOWS_EXPORT_ALL_SYMBOLS ON)

find_package(ZLIB REQUIRED CONFIG)
target_link_libraries(libid3tag PRIVATE ZLIB::ZLIB)

install(TARGETS libid3tag
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)
install(FILES id3tag.h DESTINATION include)
