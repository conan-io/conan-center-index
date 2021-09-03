import os
from conans import ConanFile, tools, CMake
from conans.errors import ConanException, ConanInvalidConfiguration


class ZlibConan(ConanFile):
    name = "dummy"
    version = "1.2.11"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://zlib.net"
    license = "Zlib"
    description = ("A Massively Spiffy Yet Delicately Unobtrusive Compression Library "
                   "(Also Free, Not to Mention Unencumbered by Patents)")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = ["CMakeLists.txt", "CMakeLists_minizip.txt", "patches/**"]
    generators = "cmake"
    topics = ("conan", "zlib", "compression")

    def validate(self):
        if self.settings.os != "Macos":
            raise ConanInvalidConfiguration("skip")

        if self.settings.arch != "armv8":
            raise ConanInvalidConfiguration("skip")

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        # first off, check the CMake version
        self.output.warn("cmake --version")
        self.run("cmake --version")
        # check sw_vers
        self.output.warn("sw_vers -productVersion")
        self.run("sw_vers -productVersion")

        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.libs.append("zlib" if self.settings.os == "Windows" and not self.settings.os.subsystem else "z")
        self.cpp_info.names["cmake_find_package"] = "ZLIB"
        self.cpp_info.names["cmake_find_package_multi"] = "ZLIB"
