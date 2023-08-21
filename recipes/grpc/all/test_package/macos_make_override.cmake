if (CMAKE_GENERATOR MATCHES "Unix Makefiles" AND CMAKE_HOST_APPLE AND CMAKE_MAKE_PROGRAM MATCHES "/usr/bin/make")
    execute_process(
        COMMAND xcrun --find make
        OUTPUT_VARIABLE xcode_make OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_VARIABLE xcrun_error)
    if(xcode_make)
        #Override the value of `CMAKE_MAKE_PROGRAM`
        set_property(CACHE CMAKE_MAKE_PROGRAM PROPERTY VALUE "${xcode_make}")
    else()
        message(WARNING "Using /usr/bin/make may prevent execution of Conan tool_requires that require DYLD_LIBRARY_PATH"
                        " to be set at build time.")
    endif()
endif()
