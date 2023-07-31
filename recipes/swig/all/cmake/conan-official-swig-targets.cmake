find_program(SWIG_EXECUTABLE swig)
get_filename_component(SWIG_DIR ${SWIG_EXECUTABLE}/../swiglib ABSOLUTE)
mark_as_advanced(SWIG_DIR SWIG_EXECUTABLE)
