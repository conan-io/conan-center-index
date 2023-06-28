# Older versions of libpng's CMakeLists reference the ZLIB_LIBRARy
# varible which was never officially documented.
# This was fixed in which first went into version 1.6.38.
# This can be deleted once the recipe no longer supports versions older than that.
# https://github.com/glennrp/libpng/commit/9f734b13f4ea062af98652c4c7678f667d2d85c7
find_package(ZLIB CONFIG REQUIRED)
set(ZLIB_LIBRARY "${ZLIB_LIBRARIES}")
