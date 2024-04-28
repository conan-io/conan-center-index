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
        "with_ssl": [False, "openssl", "darwinssl", "winssl"],
        "signal": [True, False],
        "verbose_logging": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": "openssl",
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
                "gcc": "7",
                "clang": "7",
                "apple-clang": "10",
                "Visual Studio": "15",
                "msvc": "191",
            },
        }.get(self._min_cppstd, {})

    @property
    def _uses_valid_abi_and_compiler(self):
        # https://github.com/conan-io/conan-center-index/pull/5194#issuecomment-821908385
        return not (
            self.settings.compiler == "clang"
            and self.settings.compiler.libcxx == "libstdc++"
            and Version(self.settings.compiler.version) < "9"
        )

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            self.options.with_ssl = "winssl"

        if is_apple_os(self):
            self.options.with_ssl = "darwinssl"

        if Version(self.version) < "1.10.0":
            del self.options.verbose_logging

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libcurl/[>=7.78.0 <9]", transitive_headers=True, transitive_libs=True)
        if self.options.with_ssl == "openssl":
            self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if not self._uses_valid_abi_and_compiler:
            raise ConanInvalidConfiguration(f"Cannot compile {self.ref} with libstdc++ on clang < 9")

        if self.options.with_ssl:
            ssl_library = str(self.options.with_ssl)

            if ssl_library == "openssl" and is_apple_os(self):
                raise ConanInvalidConfiguration("OpenSSL is not supported on macOS. Use DarwinSSL instead.")
            if ssl_library == "darwinssl" and not is_apple_os(self):
                raise ConanInvalidConfiguration("DarwinSSL is only supported on macOS")
            if ssl_library == "winssl" and self.settings.os != "Windows":
                raise ConanInvalidConfiguration("WinSSL is only on Windows")

        if self.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Visual Studio build for shared library with MT runtime is not supported")

        if Version(self.version) >= "1.9.0" and self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "6":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support gcc < 6")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) >= "1.10.0":
            tc.variables["CPR_USE_SYSTEM_CURL"] = True
        else:
            tc.variables["CPR_FORCE_USE_SYSTEM_CURL"] = True
        tc.variables["CPR_BUILD_TESTS"] = False
        tc.variables["CPR_GENERATE_COVERAGE"] = False
        tc.variables["CPR_USE_SYSTEM_GTEST"] = False
        tc.variables["CPR_CURL_NOSIGNAL"] = not self.options.signal
        tc.variables["CPR_FORCE_DARWINSSL_BACKEND"] = (self.options.with_ssl == "darwinssl")
        tc.variables["CPR_FORCE_OPENSSL_BACKEND"] = (self.options.with_ssl == "openssl")
        tc.variables["CPR_FORCE_WINSSL_BACKEND"] = (self.options.with_ssl == "winssl")
        tc.variables["CMAKE_USE_OPENSSL"] = (self.options.with_ssl == "openssl")
        tc.variables["CPR_ENABLE_SSL"] = bool(self.options.with_ssl)

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
