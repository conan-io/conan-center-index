from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.32.0"


class RedisPlusPlusConan(ConanFile):
    name = "redis-plus-plus"
    homepage = "https://github.com/sewenew/redis-plus-plus"
    description = "Redis client written in C++"
    topics = ("conan", "database", "redis", "client", "tls")
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package_multi"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_tls": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_tls": False
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
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def requirements(self):
        self.requires("hiredis/1.0.0")

    def validate(self):
        if self.options.with_tls != self.options["hiredis"].with_ssl:
            raise ConanInvalidConfiguration("with_tls must match hiredis.with_ssl option")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["REDIS_PLUS_PLUS_USE_TLS"] = self.options.with_tls
            self._cmake.definitions["REDIS_PLUS_PLUS_BUILD_TEST"] = False
            self._cmake.definitions["REDIS_PLUS_PLUS_BUILD_STATIC"] = not self.options.shared
            self._cmake.definitions["REDIS_PLUS_PLUS_BUILD_SHARED"] = self.options.shared
            if tools.Version(self.version) >= "1.2.3":
                self._cmake.definitions["REDIS_PLUS_PLUS_BUILD_STATIC_WITH_PIC"] = self.options.shared
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if tools.Version(self.version) < "1.2.3":
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                  "set_target_properties(${STATIC_LIB} PROPERTIES POSITION_INDEPENDENT_CODE ON)",
                                  "")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        # Introduced in 1.2.3
        self.cpp_info.names["cmake_find_package"] = "redis++"
        self.cpp_info.names["cmake_find_package_multi"] = "redis++"
        self.cpp_info.names["pkg_config"] = "redis++"
        self.cpp_info.components["redis++lib"].names["cmake_find_package"] = "redis++" + "_static" if not self.options.shared else ""
        self.cpp_info.components["redis++lib"].names["cmake_find_package_multi"] = "redis++" + "_static" if not self.options.shared else ""

        suffix = "_static" if self.settings.os == "Windows" and not self.options.shared else ""
        self.cpp_info.components["redis++lib"].libs = ["redis++" + suffix]
        self.cpp_info.components["redis++lib"].requires = ["hiredis::hiredis"]
        if self.options.with_tls:
            self.cpp_info.components["redis++lib"].requires.append("hiredis::hiredis_ssl")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["redis++lib"].system_libs.append("pthread")
