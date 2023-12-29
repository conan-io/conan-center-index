# Inject Iconv dependency with suitably-named variables
find_package(Iconv CONFIG)
set(ICONV_FOUND ${Iconv_FOUND})
set(ICONV_INCLUDE_DIR ${Iconv_INCLUDE_DIRS})
set(ICONV_LIBRARIES ${Iconv_LIBRARIES})
