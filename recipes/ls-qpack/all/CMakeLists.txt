cmake_minimum_required(VERSION 3.15)
project(cmake_wrapper)

add_subdirectory(src)

install(
    TARGETS ls-qpack
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)
install(FILES src/lsqpack.h DESTINATION include)

if(WIN32)
    install(DIRECTORY src/wincompat DESTINATION include)
endif()
