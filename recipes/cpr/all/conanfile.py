from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class CprConan(ConanFile):
    _AUTO_SSL = "auto"
    _NO_SSL = "off"

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
        "with_openssl": [True, False, "deprecated"],
        "with_winssl": [True, False, "deprecated"],
        "with_ssl": ["openssl", "darwinssl", "winssl", _AUTO_SSL, _NO_SSL]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": "deprecated",
        "with_winssl": "deprecated",
        "with_ssl": _AUTO_SSL
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
        return tools.Version(self.version) >= "1.5.0" and not tools.is_apple_os(self.settings.os)

    @property
    def _supports_winssl(self):
        # https://github.com/whoshuu/cpr/commit/18e1fc5c3fc0ffc07695f1d78897fb69e7474ea9
        # https://github.com/whoshuu/cpr/releases/tag/1.5.1
        return tools.Version(self.version) >= "1.5.1" and self.settings.os == "Windows"

    @property
    def _supports_darwinssl(self):
        # https://github.com/whoshuu/cpr/releases/tag/1.6.1
        return tools.Version(self.version) >= "1.6.1" and tools.is_apple_os(self.settings.os)

    @property
    def _can_auto_ssl(self):
        # https://github.com/whoshuu/cpr/releases/tag/1.6.0
        return not self._uses_old_cmake_options and not (
           #  https://github.com/whoshuu/cpr/issues/546
            tools.Version(self.version) in ["1.6.0", "1.6.1"]
            and tools.is_apple_os(self.settings.os)
        )


    @property
    def _uses_old_cmake_options(self):
        # https://github.com/whoshuu/cpr/releases/tag/1.6.0
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        ssl_library = self._get_ssl_library()
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
        if not self._supports_openssl:
            del self.options.with_openssl
        if not self._supports_winssl:
            del self.options.with_winssl


    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("cpr-{}".format(self.version), self._source_subfolder)

    def requirements(self):
        self.requires("libcurl/{}".format("7.67.0" if not self._supports_openssl else "7.69.1"))

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
            "CPR_GENERATE_COVERAGE": "GENERATE_COVERAGE",
        }

        if self._uses_old_cmake_options:
            # Get the translated option if we can, or the original if one isn't defined.
            return CPR_1_6_CMAKE_OPTIONS_TO_OLD.get(option, option)
        else:
            return option

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions[self._get_cmake_option("CPR_FORCE_USE_SYSTEM_CURL")] = True
            self._cmake.definitions[self._get_cmake_option("CPR_BUILD_TESTS")] = False
            self._cmake.definitions[self._get_cmake_option("CPR_GENERATE_COVERAGE")] = False
            self._cmake.definitions[self._get_cmake_option("CPR_USE_SYSTEM_GTEST")] = False

            ssl_value = self._get_ssl_library()
            SSL_OPTIONS = {
                "CPR_FORCE_DARWINSSL_BACKEND": ssl_value == "darwinssl",
                "CPR_FORCE_OPENSSL_BACKEND": ssl_value == "openssl",
                "CPR_FORCE_WINSSL_BACKEND": ssl_value == "winssl",
                "CMAKE_USE_OPENSSL": ssl_value == "openssl"
            }

            for cmake_option, value in SSL_OPTIONS.items():
                self._cmake.definitions[self._get_cmake_option(cmake_option)] = value

            # If we are on a version where disabling SSL requires a cmake option, disable it
            if not self._uses_old_cmake_options and self._get_ssl_library() == CprConan._NO_SSL:
                self._cmake.definitions["CPR_ENABLE_SSL"] = False

            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

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

    def _print_deprecation_messages(self):
        if self.options.get_safe("with_openssl") != "deprecated":
            self.output.warn("with_openssl is deprecated. Please use the with_ssl option.")
        elif self.options.get_safe("with_winssl") != "deprecated":
            self.output.warn("with_winssl is deprecated. Please use the with_ssl option.")

    # Get the configured ssl library
    def _get_ssl_library(self):
        ssl_library = str(self.options.get_safe("with_ssl"))
        # These must check for True so that we don't take "deprecated" to be truthy
        if self.options.get_safe("with_openssl") == True:
            return "openssl"
        elif self.options.get_safe("with_winssl") == True:
            return "winssl"

        return ssl_library

    def validate(self):
        SSL_FAILURE_MESSAGES = {
            "openssl": "OpenSSL is not supported on macOS or on CPR versions < 1.5.0",
            "darwinssl": "DarwinSSL is only supported on macOS and on CPR versions >= 1.6.1",
            "winssl": "WinSSL is only on Windows and on CPR versions >= 1.5.1",
            CprConan._AUTO_SSL: "Automatic SSL selection is only available on CPR versions >= 1.6.0 (and only >= 1.6.2 on macOS)"
        }

        self._print_deprecation_messages()
        if not self._uses_valid_abi_and_compiler:
            raise ConanInvalidConfiguration("Cannot compile cpr/1.6.0 with libstdc++ on clang < 9")

        ssl_library = self._get_ssl_library()
        if not self._supports_ssl_library(ssl_library):
            raise ConanInvalidConfiguration(
                "Invalid SSL selection for the given configuration: {}".format(SSL_FAILURE_MESSAGES[ssl_library])
                if ssl_library in SSL_FAILURE_MESSAGES
                else "Invalid value of ssl option, {}".format(ssl_library)
            )

        if ssl_library not in (CprConan._AUTO_SSL, CprConan._NO_SSL) and ssl_library != self.options["libcurl"].with_ssl:
            raise ConanInvalidConfiguration("cpr requires libcurl to be built with the option with_ssl='{}'.".format(self.options.get_safe('ssl')))

        if self.settings.compiler == "Visual Studio" and self.options.shared and "MT" in self.settings.compiler.runtime:
            raise ConanInvalidConfiguration("Visual Studio build for shared library with MT runtime is not supported")


    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["cpr"]
