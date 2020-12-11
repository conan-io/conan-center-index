from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class CprConan(ConanFile):
    name = "cpr"
    description = "C++ Requests: Curl for People, a spiritual port of Python Requests"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://whoshuu.github.io/cpr/"
    license = "MIT"
    topics = ("conan", "cpr", "requests", "web", "curl")
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
        "with_winssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": True,
        "with_winssl": False,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _supports_openssl(self):
        # https://github.com/whoshuu/cpr/commit/b036a3279ba62720d1e43362d32202bf412ea152
        # https://github.com/whoshuu/cpr/releases/tag/1.5.0
        return tools.Version(self.version) >= "1.5.0"

    @property
    def _supports_winssl(self):
        # https://github.com/whoshuu/cpr/commit/18e1fc5c3fc0ffc07695f1d78897fb69e7474ea9
        # https://github.com/whoshuu/cpr/releases/tag/1.5.1
        return tools.Version(self.version) >= "1.5.1"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self._supports_openssl:
            del self.options.with_openssl
        if not self._supports_winssl:
            del self.options.with_winssl

        if self._supports_openssl and tools.is_apple_os(self.settings.os):
            self.options.with_openssl = False # Default libcurl in CCI is `with_ssl="darwin"` which is unclear if cpr supports this
            
        # Make sure libcurl uses the same SSL implementation
        if self.options.get_safe("with_openssl", False):
            # self.options["libcurl"].with_openssl = True # deprecated in https://github.com/conan-io/conan-center-index/pull/2880
            self.options["libcurl"].with_ssl = "openssl"
        if self.options.get_safe("with_winssl", False):
            # self.options["libcurl"].with_winssl = True # deprecated in https://github.com/conan-io/conan-center-index/pull/2880
            self.options["libcurl"].with_ssl = "schannel"

        if self.options.get_safe("with_winssl", False) and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("cpr only supports winssl on Windows")

        if self.options.get_safe("with_openssl", False) and self.options.get_safe("with_winssl", False):
            raise ConanInvalidConfiguration("cpr can not be built with both openssl and winssl")
            
        if self.settings.compiler == "Visual Studio" and self.options.shared and "MT" in self.settings.compiler.runtime:
            raise ConanInvalidConfiguration("Visual Studio build for shared library with MT runtime is not supported")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("cpr-{}".format(self.version), self._source_subfolder)

    def requirements(self):
        self.requires("libcurl/{}".format("7.67.0" if not self._supports_openssl else "7.69.1"))

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["USE_SYSTEM_CURL"] = True
            self._cmake.definitions["BUILD_CPR_TESTS"] = False
            self._cmake.definitions["GENERATE_COVERAGE"] = False
            self._cmake.definitions["USE_SYSTEM_GTEST"] = False
            if self._supports_openssl:
                self._cmake.definitions["CMAKE_USE_OPENSSL"] = self.options.get_safe("with_openssl", False)
            if self._supports_winssl: # The CMake options changed
                # https://github.com/whoshuu/cpr/commit/18e1fc5c3fc0ffc07695f1d78897fb69e7474ea9#diff-1e7de1ae2d059d21e1dd75d5812d5a34b0222cef273b7c3a2af62eb747f9d20aR39-R40
                self._cmake.definitions["USE_OPENSSL"] = self.options.get_safe("with_openssl", False)
                self._cmake.definitions["USE_WINSSL"] = self.options.get_safe("with_winssl", False)
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        if self.options.get_safe("with_openssl", False) and self.options["libcurl"].with_ssl != "openssl":
            raise ConanInvalidConfiguration("cpr requires libcurl to be built with the option with_ssl='openssl'.")
        if self.options.get_safe("with_winssl", False) and self.options["libcurl"].with_ssl != "openssl":
            raise ConanInvalidConfiguration("cpr requires libcurl to be built with the option with_ssl='schannel'.")

        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["cpr"]
