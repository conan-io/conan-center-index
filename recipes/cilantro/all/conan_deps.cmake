# Add link_libraries() for unvendored dependencies

find_package(Spectra REQUIRED CONFIG)
find_package(Qhull REQUIRED CONFIG)
find_package(nanoflann REQUIRED CONFIG)
find_package(tinyply REQUIRED CONFIG)

link_libraries(
    Spectra::Spectra
    Qhull::qhullstatic_r
    Qhull::qhullcpp
    nanoflann::nanoflann
    tinyply::tinyply
)
