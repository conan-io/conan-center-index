cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

find_package(OpenEXR REQUIRED)
set(ALEMBIC_USING_IMATH_3 OFF)
set(ALEMBIC_ILMBASE_FOUND 1)
set(ALEMBIC_ILMBASE_LIBS OpenEXR::OpenEXR)

add_subdirectory("source_subfolder")
