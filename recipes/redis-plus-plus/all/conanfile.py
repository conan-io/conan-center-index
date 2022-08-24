from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"

class RedisPlusPlusConan(ConanFile):
    name = "redis-plus-plus"
    homepage = "https://github.com/sewenew/redis-plus-plus"
    description = "Redis client written in C++"
    topics = ("database", "redis", "client", "tls")
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    generators = "cmake", "cmake_find_package_multi"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_tls": [True, False],
        "build_async": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_tls": False,
        "build_async": False
    }

    _cmake = None

    _compiler_required_cpp17 = {
        "Visual Studio": "16",
        "gcc": "8",
        "clang": "7",
        "apple-clang": "12.0",
    }

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

    def requirements(self):
        self.requires("hiredis/1.0.2")
        if self.options.build_async:  
            self.requires("libuv/1.44.1")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            if tools.Version(self.version) >= "1.3.0":
                tools.check_min_cppstd(self, 17)
            else:
                tools.check_min_cppstd(self, 11)

        if tools.Version(self.version) >= "1.3.0":
            minimum_version = self._compiler_required_cpp17.get(str(self.settings.compiler), False)
            if minimum_version:
                if tools.Version(self.settings.compiler.version) < minimum_version:
                    raise ConanInvalidConfiguration("{} requires C++17, which your compiler does not support.".format(self.name))
            else:
                self.output.warn("{0} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name))

        if self.options.with_tls != self.options["hiredis"].with_ssl:
            raise ConanInvalidConfiguration("with_tls must match hiredis.with_ssl option")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["REDIS_PLUS_PLUS_USE_TLS"] = self.options.with_tls
            if self.options.build_async: 
                self._cmake.definitions["REDIS_PLUS_PLUS_BUILD_ASYNC"] = "libuv"
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
        self.cpp_info.set_property("cmake_file_name", "redis++")
        self.cpp_info.set_property("cmake_target_name", "redis++::redis++" + "_static" if not self.options.shared else "")
        self.cpp_info.components["redis++lib"].set_property("cmake_target_name", "redis++" + "_static" if not self.options.shared else "")
        self.cpp_info.components["redis++lib"].set_property("pkg_config_name", "redis++" + "_static" if not self.options.shared else "")

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
