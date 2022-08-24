from conan.tools.microsoft import msvc_runtime_flag
from conan import ConanFile, tools
from conans import CMake
import functools
import os

required_conan_version = ">=1.43.0"


class JanssonConan(ConanFile):
    name = "jansson"
    description = "C library for encoding, decoding and manipulating JSON data"
    topics = ("jansson", "json", "encoding", "decoding", "manipulation")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.digip.org/jansson/"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_urandom": [True, False],
        "use_windows_cryptoapi": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_urandom": True,
        "use_windows_cryptoapi": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["JANSSON_BUILD_DOCS"] = False
        cmake.definitions["JANSSON_BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["JANSSON_EXAMPLES"] = False
        cmake.definitions["JANSSON_WITHOUT_TESTS"] = True
        cmake.definitions["USE_URANDOM"] = self.options.use_urandom
        cmake.definitions["USE_WINDOWS_CRYPTOAPI"] = self.options.use_windows_cryptoapi
        if self._is_msvc:
            cmake.definitions["JANSSON_STATIC_CRT"] = "MT" in msvc_runtime_flag(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "jansson")
        self.cpp_info.set_property("cmake_target_name", "jansson::jansson")
        self.cpp_info.set_property("pkg_config_name", "jansson")
        suffix = "_d" if self.settings.os == "Windows" and self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [f"jansson{suffix}"]
