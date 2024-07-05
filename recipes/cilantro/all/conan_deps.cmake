# Add link_libraries() for unvendored dependencies

find_package(Spectra REQUIRED CONFIG)
find_package(Qhull REQUIRED CONFIG)
find_package(nanoflann REQUIRED CONFIG)
find_package(tinyply REQUIRED CONFIG)

link_libraries(
    Spectra::Spectra
    nanoflann::nanoflann
    tinyply::tinyply
)
if(TARGET Qhull::qhull_r)
    link_libraries(Qhull::qhull_r)
else()
    link_libraries(Qhull::qhullstatic_r)
endif()
