find_program(SWIG_EXECUTABLE swig)
if(NOT SWIG_DIR)
    execute_process(COMMAND ${SWIG_EXECUTABLE} -swiglib
        OUTPUT_VARIABLE SWIG_lib_output OUTPUT_STRIP_TRAILING_WHITESPACE)
    set(SWIG_DIR ${SWIG_lib_output} CACHE STRING "Location of SWIG library" FORCE)
endif()
mark_as_advanced(SWIG_DIR SWIG_EXECUTABLE)
