import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version

required_conan_version = ">=2.0.9"


class KalshiCppConan(ConanFile):
    name = "kalshi-cpp"
    description = "C++23 client for Kalshi's Predictions API: every REST operation and WebSocket channel"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Reddimus/kalshi-cpp"
    topics = ("kalshi", "prediction-markets", "trading", "rest", "websocket")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openssl/[>=3 <4]")
        self.requires("libcurl/[>=7.78.0 <9]")
        self.requires("libwebsockets/4.5.8")
        # Header-only and used only inside the library; installed headers never include it.
        self.requires("glaze/8.4.0", visible=False)

    @property
    def _min_compiler_versions(self):
        # The oldest releases that ship std::expected and the rest of the C++23 it uses.
        return {"gcc": "13", "clang": "17", "apple-clang": "15", "msvc": "194"}

    def validate(self):
        check_min_cppstd(self, 23)
        minimum = self._min_compiler_versions.get(str(self.settings.compiler))
        if minimum and Version(self.settings.compiler.version) < minimum:
            raise ConanInvalidConfiguration(
                f"{self.ref} needs {self.settings.compiler} {minimum} or newer for C++23")
        # std::to_chars for double needs macOS 13.3.
        macos = self.settings.get_safe("os.version") if self.settings.os == "Macos" else None
        if macos and Version(macos) < "13.3":
            raise ConanInvalidConfiguration(f"{self.ref} needs macOS 13.3 or newer")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["KALSHI_USE_SYSTEM_GLAZE"] = True
        tc.cache_variables["KALSHI_BUILD_TESTS"] = False
        tc.cache_variables["KALSHI_BUILD_EXAMPLES"] = False
        tc.generate()
        CMakeDeps(self).generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        CMake(self).install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "kalshi")
        self.cpp_info.set_property("cmake_target_name", "kalshi::kalshi")
        self.cpp_info.libs = ["kalshi_api", "kalshi_ws", "kalshi_models", "kalshi_http", "kalshi_auth"]
        self.cpp_info.requires = ["openssl::ssl", "openssl::crypto", "libcurl::libcurl",
                                  "libwebsockets::libwebsockets"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["pthread"]
