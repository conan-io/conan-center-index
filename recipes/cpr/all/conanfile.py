from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building, check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class CprConan(ConanFile):
    _AUTO_SSL = "auto"
    _NO_SSL = "off"

    name = "cpr"
    description = "C++ Requests: Curl for People, a spiritual port of Python Requests"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://docs.libcpr.org/"
    topics = ("requests", "web", "curl")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": ["openssl", "darwinssl", "winssl", _AUTO_SSL, _NO_SSL],
        "signal": [True, False],
        "verbose_logging": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": _AUTO_SSL,
        "signal": True,
        "verbose_logging": False,
    }

    @property
    def _min_cppstd(self):
        return "11" if Version(self.version) < "1.10.0" else "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "17": {
                "gcc": "9",
                "clang": "7",
                "apple-clang": "10",
                "Visual Studio": "15",
                "msvc": "191",
            },
        }.get(self._min_cppstd, {})

    @property
    def _supports_openssl(self):
        # https://github.com/libcpr/cpr/commit/b036a3279ba62720d1e43362d32202bf412ea152
        # https://github.com/libcpr/cpr/releases/tag/1.5.0
        return Version(self.version) >= "1.5.0" and not is_apple_os(self)

    @property
    def _supports_winssl(self):
        # https://github.com/libcpr/cpr/commit/18e1fc5c3fc0ffc07695f1d78897fb69e7474ea9
        # https://github.com/libcpr/cpr/releases/tag/1.5.1
        return Version(self.version) >= "1.5.1" and self.settings.os == "Windows"

    @property
    def _supports_darwinssl(self):
        # https://github.com/libcpr/cpr/releases/tag/1.6.1
        return Version(self.version) >= "1.6.1" and is_apple_os(self)

    @property
    def _can_auto_ssl(self):
        # https://github.com/libcpr/cpr/releases/tag/1.6.0
        return not self._uses_old_cmake_options and not (
           #  https://github.com/libcpr/cpr/issues/546
            Version(self.version) in ["1.6.0", "1.6.1"]
            and is_apple_os(self)
        )

    @property
    def _uses_old_cmake_options(self):
        # https://github.com/libcpr/cpr/releases/tag/1.6.0
        return Version(self.version) < "1.6.0"

    @property
    def _uses_valid_abi_and_compiler(self):
        # https://github.com/conan-io/conan-center-index/pull/5194#issuecomment-821908385
        return not (
            Version(self.version) >= "1.6.0"
            and self.settings.compiler == "clang"
            and self.settings.compiler.libcxx == "libstdc++"
            and Version(self.settings.compiler.version) < "9"
        )

    def export_sources(self):
        export_conandata_patches(self)

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

        if Version(self.version) < "1.10.0":
            del self.options.verbose_logging

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libcurl/8.0.1", transitive_headers=True, transitive_libs=True)

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

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        SSL_FAILURE_MESSAGES = {
            "openssl": "OpenSSL is not supported on macOS or on CPR versions < 1.5.0",
            "darwinssl": "DarwinSSL is only supported on macOS and on CPR versions >= 1.6.1",
            "winssl": "WinSSL is only on Windows and on CPR versions >= 1.5.1",
            CprConan._AUTO_SSL: "Automatic SSL selection is only available on CPR versions >= 1.6.0 (and only >= 1.6.2 on macOS)"
        }

        if not self._uses_valid_abi_and_compiler:
            raise ConanInvalidConfiguration(f"Cannot compile {self.ref} with libstdc++ on clang < 9")

        ssl_library = str(self.options.with_ssl)
        if not self._supports_ssl_library(ssl_library):
            raise ConanInvalidConfiguration(
                f"Invalid SSL selection for the given configuration: {SSL_FAILURE_MESSAGES[ssl_library]}"
                if ssl_library in SSL_FAILURE_MESSAGES
                else f"Invalid value of ssl option, {ssl_library}"
            )

        if ssl_library not in (CprConan._AUTO_SSL, CprConan._NO_SSL, "winssl") and ssl_library != self.dependencies["libcurl"].options.with_ssl:
            raise ConanInvalidConfiguration(
                f"{self.ref}:with_ssl={self.options.with_ssl} requires libcurl:with_ssl={self.options.with_ssl}"
            )

        if ssl_library == "winssl" and self.dependencies["libcurl"].options.with_ssl != "schannel":
            raise ConanInvalidConfiguration(
                f"{self.ref}:with_ssl=winssl requires libcurl:with_ssl=schannel"
            )

        if self.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Visual Studio build for shared library with MT runtime is not supported")

        if Version(self.version) >= "1.9.0" and self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "6":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support gcc < 6")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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

        CPR_1_6_CMAKE_OPTIONS_TO_1_10 = {
            "CPR_FORCE_USE_SYSTEM_CURL": "CPR_USE_SYSTEM_CURL"
        }

        if Version(self.version) >= "1.10.0":
            return CPR_1_6_CMAKE_OPTIONS_TO_1_10.get(option, option)
        return option

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables[self._get_cmake_option("CPR_FORCE_USE_SYSTEM_CURL")] = True
        tc.variables[self._get_cmake_option("CPR_BUILD_TESTS")] = False
        tc.variables[self._get_cmake_option("CPR_GENERATE_COVERAGE")] = False
        tc.variables[self._get_cmake_option("CPR_USE_SYSTEM_GTEST")] = False
        tc.variables["CPR_CURL_NOSIGNAL"] = not self.options.signal
        ssl_value = str(self.options.get_safe("with_ssl"))
        SSL_OPTIONS = {
            "CPR_FORCE_DARWINSSL_BACKEND": ssl_value == "darwinssl",
            "CPR_FORCE_OPENSSL_BACKEND": ssl_value == "openssl",
            "CPR_FORCE_WINSSL_BACKEND": ssl_value == "winssl",
            "CMAKE_USE_OPENSSL": ssl_value == "openssl"
        }
        for cmake_option, value in SSL_OPTIONS.items():
            tc.variables[self._get_cmake_option(cmake_option)] = value
        # If we are on a version where disabling SSL requires a cmake option, disable it
        if not self._uses_old_cmake_options and str(self.options.get_safe("with_ssl")) == CprConan._NO_SSL:
            tc.variables["CPR_ENABLE_SSL"] = False

        if self.options.get_safe("verbose_logging", False):
            tc.variables["CURL_VERBOSE_LOGGING"] = True
        if cross_building(self, skip_x64_x86=True):
            tc.variables["THREAD_SANITIZER_AVAILABLE_EXITCODE"] = 1
            tc.variables["THREAD_SANITIZER_AVAILABLE_EXITCODE__TRYRUN_OUTPUT"] = 1
            tc.variables["ADDRESS_SANITIZER_AVAILABLE_EXITCODE"] = 1
            tc.variables["ADDRESS_SANITIZER_AVAILABLE_EXITCODE__TRYRUN_OUTPUT"] = 1
            tc.variables["ALL_SANITIZERS_AVAILABLE_EXITCODE"] = 1
            tc.variables["ALL_SANITIZERS_AVAILABLE_EXITCODE__TRYRUN_OUTPUT"] = 1
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cpr")
        self.cpp_info.set_property("cmake_target_name", "cpr::cpr")
        self.cpp_info.libs = ["cpr"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
