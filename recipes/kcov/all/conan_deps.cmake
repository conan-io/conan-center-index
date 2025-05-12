# Wrapper for find_package() that also adds upper-case variables and allows only Conan packages
macro(custom_find_package name)
    find_package(${name} ${ARGN} CONFIG
        # Allow only Conan packages
        NO_DEFAULT_PATH
        PATHS ${CMAKE_PREFIX_PATH}
    )
    string(TOUPPER ${name} name_upper)
    set(${name_upper}_FOUND TRUE)
    set(${name_upper}_VERSION_STRING ${${name}_VERSION_STRING})
    set(${name_upper}_INCLUDE_DIRS ${${name}_INCLUDE_DIRS})
    set(${name_upper}_INCLUDE_DIR ${${name}_INCLUDE_DIR})
    set(${name_upper}_LIBRARIES ${${name}_LIBRARIES})
    set(${name_upper}_DEFINITIONS ${${name}_DEFINITIONS})
    unset(name_upper)
endmacro()

custom_find_package(Bfd)
custom_find_package(ZLIB REQUIRED)
custom_find_package(CURL REQUIRED)

if(APPLE)
    custom_find_package(Dwarfutils REQUIRED)
    set(dwarfutils_FOUND TRUE)
else()
    custom_find_package(ElfUtils REQUIRED)
    set(Elfutils_FOUND TRUE)
    # ElfUtils also provides LibElf
    set(LibElf_FOUND TRUE)
    set(LIBELF_FOUND TRUE)
    set(LIBELF_INCLUDE_DIRS ${ElfUtils_INCLUDE_DIRS})
    set(LIBELF_LIBRARIES ${ElfUtils_LIBRARIES})
    set(LIBELF_DEFINITIONS ${ElfUtils_DEFINITIONS})
endif()
