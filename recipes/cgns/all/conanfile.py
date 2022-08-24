import os
from conans import ConanFile, CMake, tools


required_conan_version = ">=1.29.1"


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
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("CGNS-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["CGNS_ENABLE_TESTS"] = False
        self._cmake.definitions["CGNS_BUILD_TESTING"] = False
        self._cmake.definitions["CGNS_ENABLE_FORTRAN"] = False
        self._cmake.definitions["CGNS_ENABLE_HDF5"] = self.options.with_hdf5
        self._cmake.definitions["CGNS_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["CGNS_USE_SHARED"] = self.options.shared
        self._cmake.definitions["CGNS_BUILD_CGNSTOOLS"] = False
        self._cmake.configure()

        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build(target="cgns_shared" if self.options.shared else "cgns_static")

    def package(self):
        self.copy("license.txt", dst="licenses", src=self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()

        os.remove(os.path.join(self.package_folder, "include", "cgnsBuild.defs"))

    def package_info(self):
        self.cpp_info.libs = ["cgnsdll" if self.settings.os == "Windows" and self.options.shared else "cgns"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines = ["CGNSDLL=__declspec(dllimport)"] # we could instead define USE_DLL but it's too generic
