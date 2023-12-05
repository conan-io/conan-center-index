# The custom find_package() ensures that system packages are not used by accident
macro(custom_find_package name)
    string(TOUPPER ${name} name_upper)
    if(NOT DEFINED WITH_${name_upper})
        message(FATAL_ERROR "WITH_${name_upper} is not defined")
    endif()
    if(WITH_${name_upper})
        find_package(${name} ${ARGN} REQUIRED CONFIG
            # Allow only Conan packages
            NO_DEFAULT_PATH
            PATHS ${CMAKE_PREFIX_PATH}
        )
    else()
        set(CMAKE_DISABLE_FIND_PACKAGE_${name} TRUE)
        set(${name}_FOUND FALSE)
        set(${name_upper}_FOUND FALSE)
    endif()
    unset(name_upper)
endmacro()

custom_find_package(ZLIB)
custom_find_package(Freetype)
custom_find_package(LibXml2)
custom_find_package(OpenSSL)
custom_find_package(Libidn)
custom_find_package(JPEG)
custom_find_package(TIFF)
custom_find_package(PNG)
custom_find_package(Fontconfig)
