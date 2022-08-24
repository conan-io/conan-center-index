import os
import functools
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.43.0"

class EdlibConan(ConanFile):
    name = "edlib"
    description = "Lightweight, super fast C/C++ (& Python) library for " \
                  "sequence alignment using edit (Levenshtein) distance."
    topics = ("edlib", "sequence-alignment", "edit-distance", "levehnstein-distance", "alignment-path")
    license = "MIT"
    homepage = "https://github.com/Martinsos/edlib"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "5.1",
        }

    def validate(self):
        if tools.scm.Version(self, self.version) < "1.2.7":
            if self.settings.compiler.get_safe("cppstd"):
                tools.build.check_min_cppstd(self, self, 11)
            return

        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 14)

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("{}/{} requires C++14. Your compiler is unknown. Assuming it supports C++14.".format(self.name, self.version))
        elif tools.scm.Version(self, self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("{}/{} requires C++14, which your compiler does not support.".format(self.name, self.version))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = False
        cmake.definitions["EDLIB_BUILD_EXAMPLES"] = False
        cmake.definitions["EDLIB_BUILD_UTILITIES"] = False
        if tools.scm.Version(self, self.version) >= "1.2.7":
            cmake.definitions["EDLIB_ENABLE_INSTALL"] = True
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "edlib")
        self.cpp_info.set_property("cmake_target_name", "edlib::edlib")
        self.cpp_info.set_property("pkg_config_name", "edlib-{}".format(tools.scm.Version(self, self.version).major))
        self.cpp_info.names["pkg_config"] = "edlib-{}".format(tools.scm.Version(self, self.version).major)
        self.cpp_info.libs = ["edlib"]
        if self.options.shared:
            self.cpp_info.defines = ["EDLIB_SHARED"]
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.system_libs = [tools.stdcpp_library(self)]
