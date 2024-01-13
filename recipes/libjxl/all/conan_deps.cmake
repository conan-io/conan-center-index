find_package(Brotli REQUIRED CONFIG)
find_package(HWY REQUIRED CONFIG)
find_package(LCMS2 REQUIRED CONFIG)

# Add wrapper targets for the project to link against
add_library(brotlicommon INTERFACE)
target_link_libraries(brotlicommon INTERFACE brotli::brotli)
set_target_properties(brotlicommon PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "${Brotli_INCLUDE_DIRS}")
set_target_properties(brotlicommon PROPERTIES INCLUDE_DIRECTORIES "${Brotli_INCLUDE_DIRS}")
add_library(brotlidec ALIAS brotlicommon)
add_library(brotlienc ALIAS brotlicommon)
add_library(brotlicommon-static ALIAS brotlicommon)
add_library(brotlidec-static ALIAS brotlicommon)
add_library(brotlienc-static ALIAS brotlicommon)

add_library(hwy INTERFACE)
target_link_libraries(hwy INTERFACE highway::highway)
set_target_properties(hwy PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "${HWY_INCLUDE_DIRS}")
set_target_properties(hwy PROPERTIES INCLUDE_DIRECTORIES "${HWY_INCLUDE_DIRS}")

add_library(lcms2 INTERFACE)
target_link_libraries(lcms2 INTERFACE lcms::lcms)
set_target_properties(lcms2 PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "${LCMS2_INCLUDE_DIRS}")
set_target_properties(lcms2 PROPERTIES INCLUDE_DIRECTORIES "${LCMS2_INCLUDE_DIRS}")
