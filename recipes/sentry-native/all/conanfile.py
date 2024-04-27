from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.microsoft import is_msvc
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
        "crashpad_with_tls": ["openssl", False],
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
        "crashpad_with_tls": "openssl",
        "with_breakpad": "sentry",
        "wer": False
    }

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _minimum_compilers_version(self):
        minimum_gcc_version = "5"
        if self.options.get_safe("backend") == "breakpad" or self.options.get_safe("backend") == "crashpad":
            minimum_gcc_version = "7"
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": minimum_gcc_version,
            "clang": "3.4",
            "apple-clang": "5.1",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if self.settings.os != "Windows" or Version(self.version) < "0.6.0":
            del self.options.wer

        # Configure default transport
        if self.settings.os == "Windows":
            self.options.backend = "crashpad"
            self.options.transport = "winhttp"
        elif self.settings.os == "Android":
            self.options.transport = "none"

        # Configure default backend
        # See https://github.com/getsentry/sentry-native/pull/927
        if self.settings.os == "Macos":
            self.options.backend = "crashpad"
        if self.settings.os in ("FreeBSD", "Linux"):
            self.options.backend = "breakpad" if Version(self.version) < "0.7.0" else "crashpad"
        if self.settings.os not in ("Linux", "Android") or self.options.backend != "crashpad" or self.options.with_crashpad != "sentry":
            del self.options.crashpad_with_tls

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
            self.requires("libcurl/[>=7.78.0 <9]")
        if self.options.backend == "crashpad":
            if self.options.with_crashpad == "google":
                self.requires("crashpad/cci.20220219")
            else:
                self.requires("zlib/[>=1.2.11 <2]")
                if self.options.get_safe("crashpad_with_tls"):
                    self.requires("openssl/[>=1.1 <4]")
        elif self.options.backend == "breakpad":
            if self.options.with_breakpad == "google":
                self.requires("breakpad/cci.20210521")
        if self.options.get_safe("qt"):
            self.requires("qt/5.15.11")
            self.requires("openssl/[>=1.1 <4]")

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

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.tool_requires("cmake/[>=3.16.4 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version])

    def generate(self):
        VirtualBuildEnv(self).generate()
        tc = CMakeToolchain(self)
        tc.variables["SENTRY_BACKEND"] = self.options.backend
        # See https://github.com/getsentry/sentry-native/pull/928
        if Version(self.version) < "0.7.0" and self.options.backend == "crashpad":
            tc.variables["SENTRY_CRASHPAD_SYSTEM"] = self.options.with_crashpad == "google"
        if self.options.backend == "breakpad":
            tc.variables["SENTRY_BREAKPAD_SYSTEM"] = self.options.with_breakpad == "google"
        tc.variables["SENTRY_ENABLE_INSTALL"] = True
        tc.variables["SENTRY_TRANSPORT"] = self.options.transport
        tc.variables["SENTRY_PIC"] = self.options.get_safe("fPIC", True)
        tc.variables["SENTRY_BUILD_TESTS"] = False
        tc.variables["SENTRY_BUILD_EXAMPLES"] = False
        tc.variables["SENTRY_INTEGRATION_QT"] = self.options.qt
        if self.options.get_safe("wer", False):
            tc.variables["CRASHPAD_WER_ENABLED"] = True
        tc.generate()
        CMakeDeps(self).generate()

    def build(self):
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

        self.cpp_info.components["sentry"].set_property("cmake_target_name", "sentry::sentry")
        self.cpp_info.components["sentry"].libs = ["sentry"]

        if self.settings.os in ("Android", "FreeBSD", "Linux"):
            self.cpp_info.components["sentry"].exelinkflags = ["-Wl,-E,--build-id=sha1"]
            self.cpp_info.components["sentry"].sharedlinkflags = ["-Wl,-E,--build-id=sha1"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["sentry"].system_libs = ["pthread", "dl"]
        elif is_apple_os(self):
            self.cpp_info.components["sentry"].frameworks = ["CoreGraphics", "CoreText"]
        elif self.settings.os == "Android":
            self.cpp_info.components["sentry"].system_libs = ["dl", "log"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["sentry"].system_libs = ["shlwapi", "dbghelp", "version"]
            if self.options.transport == "winhttp":
                self.cpp_info.components["sentry"].system_libs.append("winhttp")
        if self.options.transport == "curl":
            self.cpp_info.components["sentry"].requires.extend(["libcurl::libcurl"])
        if self.options.get_safe("qt"):
            self.cpp_info.components["sentry"].requires.extend(["qt::qt", "openssl::openssl"])

        if not self.options.shared:
            self.cpp_info.components["sentry"].defines = ["SENTRY_BUILD_STATIC"]

        if self.options.backend == "breakpad" and self.options.with_breakpad == "sentry":
            self.cpp_info.components["breakpad"].set_property("cmake_target_name", "breakpad_client")
            self.cpp_info.components["breakpad"].libs = [] if self.options.shared else ["breakpad_client"]
            if is_apple_os(self):
                self.cpp_info.components["breakpad"].frameworks.append("CoreFoundation")
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["breakpad"].system_libs.append("pthread")

            self.cpp_info.components["sentry"].requires.append("breakpad")

        if self.options.backend == "crashpad" and self.options.with_crashpad == "sentry":
            # mini_chromium
            self.cpp_info.components["crashpad_mini_chromium"].set_property("cmake_target_name", "crashpad::mini_chromium")
            self.cpp_info.components["crashpad_mini_chromium"].libs = [] if self.options.shared else ["mini_chromium"]
            if self.settings.os in ("Linux", "FreeBSD"):
                self.cpp_info.components["crashpad_mini_chromium"].system_libs.append("pthread")
            elif is_apple_os(self):
                self.cpp_info.components["crashpad_mini_chromium"].frameworks = ["CoreFoundation", "Foundation", "Security"]
                if self.settings.os == "Macos":
                    self.cpp_info.components["crashpad_mini_chromium"].frameworks.extend(["ApplicationServices", "IOKit"])
                else:  # iOS
                    self.cpp_info.components["crashpad_mini_chromium"].frameworks.extend(["CoreGraphics", "CoreText"])

            # compat
            self.cpp_info.components["crashpad_compat"].set_property("cmake_target_name", "crashpad::compat")
            # On Apple crashpad_compat is an interface library
            if not is_apple_os(self):
                self.cpp_info.components["crashpad_compat"].libs = [] if self.options.shared else ["crashpad_compat"]
            if self.settings.os in ("Linux", "FreeBSD"):
                self.cpp_info.components["crashpad_compat"].system_libs.append("dl")

            # util
            self.cpp_info.components["crashpad_util"].set_property("cmake_target_name", "crashpad::util")
            self.cpp_info.components["crashpad_util"].libs = [] if self.options.shared else ["crashpad_util"]
            self.cpp_info.components["crashpad_util"].requires = ["crashpad_compat", "crashpad_mini_chromium", "zlib::zlib"]
            if self.settings.os in ("Linux", "FreeBSD"):
                self.cpp_info.components["crashpad_util"].system_libs.extend(["pthread", "rt"])
            elif self.settings.os == "Windows":
                self.cpp_info.components["crashpad_util"].system_libs.append("winhttp")
            elif self.settings.os == "Macos":
                self.cpp_info.components["crashpad_util"].frameworks.extend(["CoreFoundation", "Foundation", "IOKit"])
                self.cpp_info.components["crashpad_util"].system_libs.append("bsm")
            if self.options.get_safe("crashpad_with_tls") == "openssl":
                self.cpp_info.components["crashpad_util"].requires.append("openssl::openssl")

            # client
            self.cpp_info.components["crashpad_client"].set_property("cmake_target_name", "crashpad::client")
            self.cpp_info.components["crashpad_client"].libs = [] if self.options.shared else ["crashpad_client"]
            self.cpp_info.components["crashpad_client"].requires = ["crashpad_util", "crashpad_mini_chromium"]

            self.cpp_info.components["sentry"].requires.append("crashpad_client")

            # snapshot
            self.cpp_info.components["crashpad_snapshot"].set_property("cmake_target_name", "crashpad::snapshot")
            self.cpp_info.components["crashpad_snapshot"].libs = [] if self.options.shared else ["crashpad_snapshot"]
            self.cpp_info.components["crashpad_snapshot"].requires = [
                "crashpad_client", "crashpad_compat",
                "crashpad_util", "crashpad_mini_chromium",
            ]
            if self.settings.os == "Windows":
                self.cpp_info.components["snapshot"].system_libs.append("powrprof")

            # minidump
            self.cpp_info.components["crashpad_minidump"].set_property("cmake_target_name", "crashpad::minidump")
            self.cpp_info.components["crashpad_minidump"].libs = [] if self.options.shared else ["crashpad_minidump"]
            self.cpp_info.components["crashpad_minidump"].requires = [
                "crashpad_compat", "crashpad_snapshot",
                "crashpad_util", "crashpad_mini_chromium",
            ]

            if self.settings.os == "Windows":
                # getopt
                self.cpp_info.components["crashpad_getopt"].set_property("cmake_target_name", "crashpad::getopt")
                self.cpp_info.components["crashpad_getopt"].libs = [] if self.options.shared else ["crashpad_getopt"]

            # handler
            self.cpp_info.components["crashpad_handler"].set_property("cmake_target_name", "crashpad::handler")
            self.cpp_info.components["crashpad_handler"].libs = [] if self.options.shared else ["crashpad_handler_lib"]
            self.cpp_info.components["crashpad_handler"].requires = [
                "crashpad_compat", "crashpad_minidump", "crashpad_snapshot",
                "crashpad_util", "crashpad_mini_chromium",
            ]
            if self.settings.os == "Windows":
                self.cpp_info.components["crashpad_handler"].requires.append("crashpad_getopt")

            # tools
            self.cpp_info.components["crashpad_tools"].set_property("cmake_target_name", "crashpad::tools")
            self.cpp_info.components["crashpad_tools"].libs = [] if self.options.shared else ["crashpad_tools"]

            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info(f"Appending PATH environment variable: {bin_path}")
            self.env_info.PATH.append(bin_path)

            # TODO: to remove in conan v2 once cmake_find_package* generators removed
            self.cpp_info.names["cmake_find_package"] = "crashpad"
            self.cpp_info.names["cmake_find_package_multi"] = "crashpad"
            self.cpp_info.components["crashpad_mini_chromium"].names["cmake_find_package"] = "mini_chromium"
            self.cpp_info.components["crashpad_mini_chromium"].names["cmake_find_package_multi"] = "mini_chromium"
            self.cpp_info.components["crashpad_compat"].names["cmake_find_package"] = "compat"
            self.cpp_info.components["crashpad_compat"].names["cmake_find_package_multi"] = "compat"
            self.cpp_info.components["crashpad_util"].names["cmake_find_package"] = "util"
            self.cpp_info.components["crashpad_util"].names["cmake_find_package_multi"] = "util"
            self.cpp_info.components["crashpad_client"].names["cmake_find_package"] = "client"
            self.cpp_info.components["crashpad_client"].names["cmake_find_package_multi"] = "client"
            self.cpp_info.components["crashpad_snapshot"].names["cmake_find_package"] = "snapshot"
            self.cpp_info.components["crashpad_snapshot"].names["cmake_find_package_multi"] = "snapshot"
            self.cpp_info.components["crashpad_minidump"].names["cmake_find_package"] = "minidump"
            self.cpp_info.components["crashpad_minidump"].names["cmake_find_package_multi"] = "minidump"
            if self.settings.os == "Windows":
                self.cpp_info.components["crashpad_getopt"].names["cmake_find_package"] = "getopt"
                self.cpp_info.components["crashpad_getopt"].names["cmake_find_package_multi"] = "getopt"
            self.cpp_info.components["crashpad_handler"].names["cmake_find_package"] = "handler"
            self.cpp_info.components["crashpad_handler"].names["cmake_find_package_multi"] = "handler"
            self.cpp_info.components["crashpad_tools"].names["cmake_find_package"] = "tools"
            self.cpp_info.components["crashpad_tools"].names["cmake_find_package_multi"] = "tools"

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "sentry"
        self.cpp_info.names["cmake_find_package_multi"] = "sentry"
