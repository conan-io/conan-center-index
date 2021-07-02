from conans import ConanFile, tools, CMake
import os
import glob


class tngConan(ConanFile):
    name = "tng"
    description = "External GROMACS library for loading tng files."
    license = "BSD-3-Clause"
    topics = ("conan", "tng", "gromacs")
    homepage = "https://gitlab.com/gromacs/tng/"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    requires = (
        "zlib/1.2.11"
    )

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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]["url"]
        extracted_dir = self.name + "-v" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["TNG_BUILD_OWN_ZLIB"] = False
        self._cmake.definitions["TNG_BUILD_EXAMPLES"] = False
        self._cmake.definitions["TNG_BUILD_TEST"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["tng_io"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["m"]
        self.cpp_info.names["cmake_find_package"] = "tng_io"
        self.cpp_info.names["cmake_find_package_multi"] = "tng_io"
