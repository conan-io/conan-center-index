from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
from conan.tools.build import cross_building
import os
import functools

required_conan_version = ">=1.43.0"


class CprConan(ConanFile):
    _AUTO_SSL = "auto"
    _NO_SSL = "off"

    name = "cpr"
    description = "C++ Requests: Curl for People, a spiritual port of Python Requests"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://docs.libcpr.org/"
    topics = ("requests", "web", "curl")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": ["openssl", "darwinssl", "winssl", _AUTO_SSL, _NO_SSL],
        "signal": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": _AUTO_SSL,
        "signal": True,
    }

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _supports_openssl(self):
        # https://github.com/libcpr/cpr/commit/b036a3279ba62720d1e43362d32202bf412ea152
        # https://github.com/libcpr/cpr/releases/tag/1.5.0
        return tools.Version(self.version) >= "1.5.0" and not tools.is_apple_os(self.settings.os)

    @property
    def _supports_winssl(self):
        # https://github.com/libcpr/cpr/commit/18e1fc5c3fc0ffc07695f1d78897fb69e7474ea9
        # https://github.com/libcpr/cpr/releases/tag/1.5.1
        return tools.Version(self.version) >= "1.5.1" and self.settings.os == "Windows"

    @property
    def _supports_darwinssl(self):
        # https://github.com/libcpr/cpr/releases/tag/1.6.1
        return tools.Version(self.version) >= "1.6.1" and tools.is_apple_os(self.settings.os)

    @property
    def _can_auto_ssl(self):
        # https://github.com/libcpr/cpr/releases/tag/1.6.0
        return not self._uses_old_cmake_options and not (
           #  https://github.com/libcpr/cpr/issues/546
            tools.Version(self.version) in ["1.6.0", "1.6.1"]
            and tools.is_apple_os(self.settings.os)
        )

    @property
    def _uses_old_cmake_options(self):
        # https://github.com/libcpr/cpr/releases/tag/1.6.0
        return tools.Version(self.version) < "1.6.0"

    @property
    def _uses_valid_abi_and_compiler(self):
        # https://github.com/conan-io/conan-center-index/pull/5194#issuecomment-821908385
        return not (
            tools.Version(self.version) >= "1.6.0"
            and self.settings.compiler == "clang"
            and self.settings.compiler.libcxx == "libstdc++"
            and tools.Version(self.settings.compiler.version) < "9"
        )

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        ssl_library = str(self.options.get_safe("with_ssl"))
        if not self._can_auto_ssl and ssl_library == CprConan._AUTO_SSL:
            if self._supports_openssl:
                self.output.info("Auto SSL is not available below version 1.6.0. Falling back to openssl")
                self.options.with_ssl = "openssl"
            else:
                self.output.info("Auto SSL is not available below version 1.6.0 (or below 1.6.2 on macOS), and openssl not supported. Disabling SSL")
                self.options.with_ssl = CprConan._NO_SSL

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("libcurl/7.80.0")

    def validate(self):
        SSL_FAILURE_MESSAGES = {
            "openssl": "OpenSSL is not supported on macOS or on CPR versions < 1.5.0",
            "darwinssl": "DarwinSSL is only supported on macOS and on CPR versions >= 1.6.1",
            "winssl": "WinSSL is only on Windows and on CPR versions >= 1.5.1",
            CprConan._AUTO_SSL: "Automatic SSL selection is only available on CPR versions >= 1.6.0 (and only >= 1.6.2 on macOS)"
        }

        if not self._uses_valid_abi_and_compiler:
            raise ConanInvalidConfiguration("Cannot compile cpr/1.6.0 with libstdc++ on clang < 9")

        ssl_library = str(self.options.get_safe("with_ssl"))
        if not self._supports_ssl_library(ssl_library):
            raise ConanInvalidConfiguration(
                "Invalid SSL selection for the given configuration: {}".format(SSL_FAILURE_MESSAGES[ssl_library])
                if ssl_library in SSL_FAILURE_MESSAGES
                else "Invalid value of ssl option, {}".format(ssl_library)
            )

        if ssl_library not in (CprConan._AUTO_SSL, CprConan._NO_SSL, "winssl") and ssl_library != self.options["libcurl"].with_ssl:
            raise ConanInvalidConfiguration("cpr requires libcurl to be built with the option with_ssl='{}'.".format(self.options.get_safe('with_ssl')))

        if ssl_library == "winssl" and self.options["libcurl"].with_ssl != "schannel":
            raise ConanInvalidConfiguration("cpr requires libcurl to be built with the option with_ssl='schannel'")

        if is_msvc(self) and self.options.shared and "MT" in self.settings.compiler.runtime:
            raise ConanInvalidConfiguration("Visual Studio build for shared library with MT runtime is not supported")

        if tools.Version(self.version) == "1.9.0" and self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "6":
            raise ConanInvalidConfiguration("{}/{} doesn't support gcc < 6".format(self.name, self.version))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _get_cmake_option(self, option):
        CPR_1_6_CMAKE_OPTIONS_TO_OLD = {
            "CPR_FORCE_USE_SYSTEM_CURL": "USE_SYSTEM_CURL",
            "CPR_BUILD_TESTS": "BUILD_CPR_TESTS",
            "CPR_BUILD_TESTS_SSL": "BUILD_CPR_TESTS_SSL",
            "CPR_GENERATE_COVERAGE": "GENERATE_COVERAGE",
            "CPR_USE_SYSTEM_GTEST": "USE_SYSTEM_GTEST",
            "CPR_FORCE_OPENSSL_BACKEND": "USE_OPENSSL",
            "CPR_FORCE_WINSSL_BACKEND": "USE_WINSSL",
        }

        if self._uses_old_cmake_options:
            # Get the translated option if we can, or the original if one isn't defined.
            return CPR_1_6_CMAKE_OPTIONS_TO_OLD.get(option, option)
        else:
            return option

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions[self._get_cmake_option("CPR_FORCE_USE_SYSTEM_CURL")] = True
        cmake.definitions[self._get_cmake_option("CPR_BUILD_TESTS")] = False
        cmake.definitions[self._get_cmake_option("CPR_GENERATE_COVERAGE")] = False
        cmake.definitions[self._get_cmake_option("CPR_USE_SYSTEM_GTEST")] = False
        cmake.definitions["CPR_CURL_NOSIGNAL"] = not self.options.signal

        ssl_value = str(self.options.get_safe("with_ssl"))
        SSL_OPTIONS = {
            "CPR_FORCE_DARWINSSL_BACKEND": ssl_value == "darwinssl",
            "CPR_FORCE_OPENSSL_BACKEND": ssl_value == "openssl",
            "CPR_FORCE_WINSSL_BACKEND": ssl_value == "winssl",
            "CMAKE_USE_OPENSSL": ssl_value == "openssl"
        }

        for cmake_option, value in SSL_OPTIONS.items():
            cmake.definitions[self._get_cmake_option(cmake_option)] = value

        # If we are on a version where disabling SSL requires a cmake option, disable it
        if not self._uses_old_cmake_options and str(self.options.get_safe("with_ssl")) == CprConan._NO_SSL:
            cmake.definitions["CPR_ENABLE_SSL"] = False

        if hasattr(self, "settings_build") and cross_building(self, skip_x64_x86=True):
            cmake.definitions["THREAD_SANITIZER_AVAILABLE_EXITCODE"] = 1
            cmake.definitions["THREAD_SANITIZER_AVAILABLE_EXITCODE__TRYRUN_OUTPUT"] = 1
            cmake.definitions["ADDRESS_SANITIZER_AVAILABLE_EXITCODE"] = 1
            cmake.definitions["ADDRESS_SANITIZER_AVAILABLE_EXITCODE__TRYRUN_OUTPUT"] = 1
            cmake.definitions["ALL_SANITIZERS_AVAILABLE_EXITCODE"] = 1
            cmake.definitions["ALL_SANITIZERS_AVAILABLE_EXITCODE__TRYRUN_OUTPUT"] = 1

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    # Check if the system supports the given ssl library
    def _supports_ssl_library(self, library):
        if library == CprConan._NO_SSL:
            return True
        elif library == CprConan._AUTO_SSL:
            return self._can_auto_ssl

        validators = {
            "openssl": self._supports_openssl,
            "darwinssl": self._supports_darwinssl,
            "winssl": self._supports_winssl,
            CprConan._AUTO_SSL: self._can_auto_ssl
        }

        # A KeyError should never happen, as the options are validated by conan.
        return validators[library]

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["cpr"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        self.cpp_info.set_property("cmake_target_name", "cpr::cpr")

        self.cpp_info.names["cmake_find_package"] = "cpr"
        self.cpp_info.names["cmake_find_package_multi"] = "cpr"
