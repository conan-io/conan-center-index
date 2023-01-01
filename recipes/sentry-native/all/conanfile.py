from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.43.0"


class SentryNativeConan(ConanFile):
    name = "sentry-native"
    description = (
        "The Sentry Native SDK is an error and crash reporting client for native "
        "applications, optimized for C and C++. Sentry allows to add tags, "
        "breadcrumbs and arbitrary custom context to enrich error reports."
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/getsentry/sentry-native"
    license = "MIT"
    topics = ("breakpad", "crashpad", "error-reporting", "crash-reporting")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "backend": ["none", "inproc", "crashpad", "breakpad"],
        "transport": ["none", "curl", "winhttp"],
        "qt": [True, False],
        "with_crashpad": ["google", "sentry"],
        "with_breakpad": ["google", "sentry"],
        "performance": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "backend": "inproc",  # overwritten in config_options
        "transport": "curl",  # overwritten in config_options
        "qt": False,
        "with_crashpad": "sentry",
        "with_breakpad": "sentry",
        "performance": False,
    }

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        # Configure default transport
        if self.settings.os == "Windows":
            self.options.transport = "winhttp"
        elif self.settings.os in ("FreeBSD", "Linux") or self.settings.os == "Macos":  # Don't use tools.is_apple_os(os) here
            self.options.transport = "curl"
        else:
            self.options.transport = "none"

        # Configure default backend
        if self.settings.os in ('Windows', 'Macos'):  # Don't use is_apple_os(os) here
            # FIXME: for self.version < 0.4: default backend is "breakpad" when building with MSVC for Windows xp; else: backend=none
            self.options.backend = "crashpad"
        elif self.settings.os in ("FreeBSD", "Linux"):
            self.options.backend = "breakpad"
        elif self.settings.os == "Android":
            self.options.backend = "inproc"
        else:
            self.options.backend = "inproc"

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.backend != "crashpad":
            self.options.rm_safe("with_crashpad")
        if self.options.backend != "breakpad":
            self.options.rm_safe("with_breakpad")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.transport == "curl":
            self.requires("libcurl/7.86.0")
        if self.options.backend == "crashpad":
            if self.options.with_crashpad == "sentry":
                self.requires(f"sentry-crashpad/{self.version}")
            if self.options.with_crashpad == "google":
                self.requires("crashpad/cci.20210507")
        elif self.options.backend == "breakpad":
            if self.options.with_breakpad == "sentry":
                self.requires(f"sentry-breakpad/{self.version}")
            if self.options.with_breakpad == "google":
                self.requires("breakpad/cci.20210521")
        if self.options.qt:
            self.requires("qt/5.15.7")
            self.requires("openssl/1.1.1s")
            if Version(self.version) < "0.4.5":
                raise ConanInvalidConfiguration("Qt integration available from version 0.4.5")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 14)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("Compiler is unknown. Assuming it supports C++14.")
        elif Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"Build requires support for C++14. Minimum version for {self.settings.compiler} is {minimum_version}")
        if self.options.backend == "inproc" and self.settings.os == "Windows" and Version(self.version) < "0.4":
            raise ConanInvalidConfiguration("The in-process backend is not supported on Windows")
        if self.options.transport == "winhttp" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("The winhttp transport is only supported on Windows")
        if Version(self.version) >= "0.4.7" and self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) < "10.0":
            raise ConanInvalidConfiguration("apple-clang < 10.0 not supported")
        if self.options.backend == "crashpad" and Version(self.version) < "0.4.7" and self.settings.os == "Macos" and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration("This version doesn't support ARM compilation")

        if self.options.performance:
            if Version(self.version) < "0.4.14" or Version(self.version) > "0.4.15":
                raise ConanInvalidConfiguration("Performance monitoring is only valid in 0.4.14 and 0.4.15")

    def build_requirements(self):
        if Version(self.version) >= "0.4.0" and self.settings.os == "Windows":
            self.build_requires("cmake/3.22.0")
        if self.options.backend == "breakpad":
            self.build_requires("pkgconf/1.7.4")

    def source(self):
        get(self, **self.conan_data["sources"][self.version])

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PACKAGE_CUSTOM_DEFINITION"] = True
        tc.variables["SENTRY_BACKEND"] = self.options.backend
        tc.variables["SENTRY_CRASHPAD_SYSTEM"] = True
        tc.variables["SENTRY_BREAKPAD_SYSTEM"] = True
        tc.variables["SENTRY_ENABLE_INSTALL"] = True
        tc.variables["SENTRY_TRANSPORT"] = self.options.transport
        tc.variables["SENTRY_PIC"] = self.options.get_safe("fPIC", True)
        tc.variables["SENTRY_INTEGRATION_QT"] = self.options.qt
        tc.variables["SENTRY_PERFORMANCE_MONITORING"] = self.options.performance
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, pattern="*pdb", folder=os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "sentry")
        self.cpp_info.set_property("cmake_target_name", "sentry::sentry")
        self.cpp_info.libs = ["sentry"]
        if self.settings.os in ("Android", "FreeBSD", "Linux"):
            self.cpp_info.exelinkflags = ["-Wl,-E,--build-id=sha1"]
            self.cpp_info.sharedlinkflags = ["-Wl,-E,--build-id=sha1"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread", "dl"]
        elif self.settings.os == "Android":
            self.cpp_info.system_libs = ["dl", "log"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["shlwapi", "dbghelp"]
            if Version(self.version) >= "0.4.7":
                self.cpp_info.system_libs.append("Version")
            if self.options.transport == "winhttp":
                self.cpp_info.system_libs.append("winhttp")

        if not self.options.shared:
            self.cpp_info.defines = ["SENTRY_BUILD_STATIC"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "sentry"
        self.cpp_info.names["cmake_find_package_multi"] = "sentry"
