import os
from pathlib import Path

from conans import ConanFile, CMake, tools


class CgnsConan(ConanFile):
    name = "cgns"
    description = "Standard for data associated with the numerical solution " \
                  "of fluid dynamics equations."
    topics = ("conan", "cgns", "data", "cfd", "fluids")
    homepage = "http://cgns.org/"
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_hdf5": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_hdf5": True
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_hdf5:
            self.requires("hdf5/1.12.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("CGNS-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["CGNS_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["CGNS_ENABLE_HDF5"] = self.options.with_hdf5
        self._cmake.configure()

        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("license.txt", dst="licenses", src=self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()

        for binary in Path(self.package_folder, "bin").iterdir():
            if binary.suffix != ".dll":
                binary.unlink()

        Path(self.package_folder, "include", "cgnsBuild.defs").unlink()

    def package_info(self):
        # FIXME: CGNS does not install under a CMake namespace https://github.com/CGNS/CGNS/blob/7cc605021cc6c278acf2e69c5c3bd69ff5ee504e/src/CMakeLists.txt#L648-L654
        self.cpp_info.names["cmake_find_package"] = "CGNS"
        self.cpp_info.names["cmake_find_package_multi"] = "CGNS"

        # Although CGNS defines the targets cgns_static and cgns_shared,
        # the output name is always cgns or cgnsdll
        self.cpp_info.libs = tools.collect_libs(self)
