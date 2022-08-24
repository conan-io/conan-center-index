from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import functools

required_conan_version = ">=1.43.0"

class FastPFORConan(ConanFile):
    name = "fastpfor"
    description = "Fast integer compression"
    topics = ("compression", "sorted-lists", "simd", "x86", "x86-64")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lemire/FastPFor"
    license = "Apache-2.0"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
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

    def validate(self):
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("{} architecture is not supported".format(self.settings.arch))

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "11")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["FastPFOR"]

        self.cpp_info.set_property("cmake_file_name", "FastPFOR")
        self.cpp_info.set_property("cmake_target_name", "FastPFOR::FastPFOR")

        self.cpp_info.filenames["cmake_find_package"] = "FastPFOR"
        self.cpp_info.filenames["cmake_find_package_multi"] = "FastPFOR"
        self.cpp_info.names["cmake_find_package"] = "FastPFOR"
        self.cpp_info.names["cmake_find_package_multi"] = "FastPFOR"
