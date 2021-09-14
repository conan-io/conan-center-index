import os

from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class BloatyConan(ConanFile):
    name = "bloaty"
    description = """Bloaty McBloatface: a size profiler for binaries"""
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/bloaty"
    license = "Apache-2.0"
    topics = ("conan", "bloaty", "profiler", "size")

    settings = "os", "arch", "compiler", "build_type"

    requires = (
        "capstone/4.0.2",
        "protobuf/3.17.1",
        "pkgconf/1.7.4",
        "zlib/1.2.11",
        "re2/20210601",
        "abseil/20210324.2",
    )
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake", "cmake_find_package", "pkg_config"

    _source_subfolder = "source_subfolder"

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("bloaty package does not support Windows")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    _cmake = None

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if not tools.valid_min_cppstd(self, 11):
            self._cmake.definitions["CMAKE_CXX_STANDARD"] = 11
        env_vars = {"PKG_CONFIG_PATH": self.build_folder}
        with tools.environment_append(env_vars):
            self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
