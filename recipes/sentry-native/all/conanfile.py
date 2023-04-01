from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir, export_conandata_patches, apply_conandata_patches
from conan.tools.gnu import PkgConfigDeps
from conan.tools.scm import Version
import os

required_conan_version = ">=1.55.0"


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

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "backend": ["none", "inproc", "crashpad", "breakpad"],
        "transport": ["none", "curl", "winhttp"],
        "qt": [True, False],
        "with_crashpad": ["google", "sentry"],
        "with_breakpad": ["google", "sentry"],
        "wer" : [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "backend": "inproc",  # overwritten in config_options
        "transport": "curl",  # overwritten in config_options
        "qt": False,
        "with_crashpad": "sentry",
        "with_breakpad": "sentry",
        "wer": False
    }

    @property
    def _min_cppstd(self):
        return "14"

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
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
        if self.settings.os == "Windows" or self.settings.os == "Macos":  # Don't use tools.is_apple_os(os) here
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
            self.requires("libcurl/7.87.0")
        if self.options.backend == "crashpad":
            if self.options.with_crashpad == "sentry":
                self.requires(f"sentry-crashpad/{self.version}")
            if self.options.with_crashpad == "google":
                self.requires("crashpad/cci.20220219")
        elif self.options.backend == "breakpad":
            if self.options.with_breakpad == "sentry":
                self.requires(f"sentry-breakpad/{self.version}")
            if self.options.with_breakpad == "google":
                self.requires("breakpad/cci.20210521")
        if self.options.get_safe("qt"):
            self.requires("qt/5.15.8")
            self.requires("openssl/1.1.1t")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler doesn't support."
            )
        if self.options.transport == "winhttp" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("The winhttp transport is only supported on Windows")
        if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) < "10.0":
            raise ConanInvalidConfiguration("apple-clang < 10.0 not supported")

    def _cmake_new_enough(self, required_version):
        try:
            import re
            from io import StringIO
            output = StringIO()
            self.run("cmake --version", output)
            m = re.search(r"cmake version (\d+\.\d+\.\d+)", output.getvalue())
            return Version(m.group(1)) >= required_version
        except:
            return False

    def build_requirements(self):
        if self.settings.os == "Windows" and not self._cmake_new_enough("3.16.4"):
            self.tool_requires("cmake/3.25.2")
        if self.options.backend == "breakpad":
            if not self.conf.get("tools.gnu:pkg_config", check_type=str):
                self.tool_requires("pkgconf/1.9.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version])

    def generate(self):
        VirtualBuildEnv(self).generate()
        tc = CMakeToolchain(self)
        tc.variables["SENTRY_BACKEND"] = self.options.backend
        tc.variables["SENTRY_CRASHPAD_SYSTEM"] = True
        tc.variables["SENTRY_BREAKPAD_SYSTEM"] = True
        tc.variables["SENTRY_ENABLE_INSTALL"] = True
        tc.variables["SENTRY_TRANSPORT"] = self.options.transport
        tc.variables["SENTRY_PIC"] = self.options.get_safe("fPIC", True)
        tc.variables["SENTRY_INTEGRATION_QT"] = self.options.qt
        tc.variables["CRASHPAD_WER_ENABLED"] = self.options.wer
        tc.generate()
        CMakeDeps(self).generate()
        if self.options.backend == "breakpad":
            PkgConfigDeps(self).generate()

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
        rm(self, "*pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "sentry")
        self.cpp_info.set_property("cmake_target_name", "sentry::sentry")
        self.cpp_info.libs = ["sentry"]
        if self.settings.os in ("Android", "FreeBSD", "Linux"):
            self.cpp_info.exelinkflags = ["-Wl,-E,--build-id=sha1"]
            self.cpp_info.sharedlinkflags = ["-Wl,-E,--build-id=sha1"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread", "dl"]
        elif is_apple_os(self):
            self.cpp_info.frameworks = ["CoreGraphics", "CoreText"]
        elif self.settings.os == "Android":
            self.cpp_info.system_libs = ["dl", "log"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["shlwapi", "dbghelp", "version"]
            if self.options.transport == "winhttp":
                self.cpp_info.system_libs.append("winhttp")

        if not self.options.shared:
            self.cpp_info.defines = ["SENTRY_BUILD_STATIC"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "sentry"
        self.cpp_info.names["cmake_find_package_multi"] = "sentry"
