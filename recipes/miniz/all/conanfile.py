from conans import ConanFile, CMake, tools
import functools
import os

required_conan_version = ">=1.43.0"


class MinizConan(ConanFile):
    name = "miniz"
    description = "Lossless, high performance data compression library that " \
                  "implements the zlib (RFC 1950) and Deflate (RFC 1951) " \
                  "compressed data format specification standards"
    license = "MIT"
    topics = ("miniz", "compression", "lossless")
    homepage = "https://github.com/richgel999/miniz"
    url = "https://github.com/conan-io/conan-center-index"

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

    @property
    def _build_subfolder(self):
        return "build_subfolder"

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        if tools.Version(self.version) >= "2.2.0":
            cmake.definitions["BUILD_EXAMPLES"] = False
            cmake.definitions["BUILD_FUZZERS"] = False
            cmake.definitions["AMALGAMATE_SOURCES"] = False
            cmake.definitions["BUILD_HEADER_ONLY"] = False
            cmake.definitions["INSTALL_PROJECT"] = True
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "miniz")
        self.cpp_info.set_property("cmake_target_name", "miniz::miniz")
        self.cpp_info.set_property("pkg_config_name", "miniz")
        self.cpp_info.libs = ["miniz"]
        self.cpp_info.includedirs = ["include", os.path.join("include", "miniz")]
