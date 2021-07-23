from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class OpusConan(ConanFile):
    name = "opus"
    description = "Opus is a totally open, royalty-free, highly versatile audio codec."
    topics = ("conan", "opus", "audio", "decoder", "decoding", "multimedia", "sound")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://opus-codec.org"
    license = "BSD-3-Clause"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "fixed_point": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "fixed_point": False,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
             del self.options.fPIC

    def configure(self):
        if self.options.shared:
             del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) < "14":
            raise ConanInvalidConfiguration("On Windows, the opus package can only be built with "
                                            "Visual Studio 2015 or higher.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["OPUS_FIXED_POINT"] = self.options.fixed_point
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder, keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Opus"
        self.cpp_info.names["cmake_find_package_multi"] = "Opus"
        self.cpp_info.components["libopus"].libs = ["opus"]
        self.cpp_info.components["libopus"].includedirs.append(os.path.join("include", "opus"))
        self.cpp_info.components["libopus"].names["cmake_find_package"] = "opus"
        self.cpp_info.components["libopus"].names["cmake_find_package_multi"] = "opus"
        self.cpp_info.components["libopus"].names["pkg_config"] = "opus"
        if self.settings.os == "Linux" or self.settings.os == "Android":
            self.cpp_info.components["libopus"].system_libs.append("m")
        if self.settings.os == "Windows" and self.settings.compiler != "Visual Studio":
            self.cpp_info.components["libopus"].system_libs.append("ssp")
