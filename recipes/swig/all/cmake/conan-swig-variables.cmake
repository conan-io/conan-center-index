find_program(SWIG_EXECUTABLE swig)
# CMakeDeps sets SWIG_DIR to the generators folder, override it to the correct value
get_filename_component(SWIG_DIR "${SWIG_EXECUTABLE}/../swiglib" ABSOLUTE)
