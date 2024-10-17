# Replace vendored Spectra with a Conan version
find_package(spectra REQUIRED CONFIG)
link_libraries(Spectra::Spectra)
