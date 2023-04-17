import os
from conan import ConanFile, tools
from conan.tools.files import apply_conandata_patches
from conans import CMake

required_conan_version = ">=1.45.0"


class MarisaConan(ConanFile):
    name = "marisa"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/s-yata/marisa-trie"
    description = "Matching Algorithm with Recursively Implemented StorAge "
    license = ("BSD-2-Clause", "LGPL-2.1")
    topics = ("algorithm", "dictionary", "marisa")
    exports_sources = "patches/**", "CMakeLists.txt"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "tools": True,
    }

    generators = "cmake"
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
        tools.files.get(**self.conan_data["sources"][self.version],
                        conanfile=self, destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        self._cmake.definitions["BUILD_TOOLS"] = self.options.tools

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        apply_conandata_patches(self)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING.md", dst="licenses",
                  src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(
            self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "marisa"
        self.cpp_info.names["cmake_find_package_multi"] = "marisa"
        self.cpp_info.names["pkgconfig"] = "marisa"
        self.cpp_info.libs = ["marisa"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH env var with : '{bin_path}'")
        self.env_info.PATH.append(bin_path)
