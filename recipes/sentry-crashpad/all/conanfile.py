from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir, rm, replace_in_file

import os

required_conan_version = ">=2.1"


class SentryCrashpadConan(ConanFile):
    name = "sentry-crashpad"
    description = "Crashpad is a crash-reporting system."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/getsentry/sentry-native"
    license = "Apache-2.0"
    topics = ("crashpad", "error-reporting", "crash-reporting")
    provides = "crashpad", "mini_chromium"
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_tls": ["openssl", False],
    }
    default_options = {
        "fPIC": True,
        "with_tls": "openssl",
    }

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ("Linux", "Android"):
            del self.options.with_tls

    def build_requirements(self):
        if self._is_mingw:
            self.tool_requires("jwasm/2.13")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        if self.settings.os in ("Linux", "FreeBSD"):
            self.requires("libcurl/[>=7.78.0 <9]")
        if self.options.get_safe("with_tls"):
            self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        # Since 0.7, the public client headers need C++17 (getsentry/crashpad#160).
        check_min_cppstd(self, 17)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)])
        # Let Conan configure C++ standard
        replace_in_file(self, os.path.join(self.source_folder, "external", "crashpad", "CMakeLists.txt"), "set(CMAKE_CXX_STANDARD 17)", "")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CRASHPAD_ENABLE_INSTALL"] = True
        tc.variables["CRASHPAD_ENABLE_INSTALL_DEV"] = True
        tc.variables["CRASHPAD_ZLIB_SYSTEM"] = True
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="external/crashpad")
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=os.path.join(self.source_folder, "external", "crashpad"),
                              dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "crashpad")

        # mini_chromium
        self.cpp_info.components["crashpad_mini_chromium"].set_property("cmake_target_name", "crashpad::mini_chromium")
        self.cpp_info.components["crashpad_mini_chromium"].includedirs.append(os.path.join("include", "crashpad", "mini_chromium"))
        self.cpp_info.components["crashpad_mini_chromium"].libs = ["mini_chromium"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["crashpad_mini_chromium"].system_libs.append("pthread")
        elif self.settings.os == "Windows":
            # The public headers use std::min and std::max. Crashpad defines NOMINMAX only on its
            # own private target, so consumers that include <windows.h> get the min/max macros.
            self.cpp_info.components["crashpad_mini_chromium"].defines.append("NOMINMAX")
        elif is_apple_os(self):
            self.cpp_info.components["crashpad_mini_chromium"].frameworks = ["CoreFoundation", "Foundation", "Security"]
            if self.settings.os == "Macos":
                self.cpp_info.components["crashpad_mini_chromium"].frameworks.extend(["ApplicationServices", "IOKit"])
            else:  # iOS
                self.cpp_info.components["crashpad_mini_chromium"].frameworks.extend(["CoreGraphics", "CoreText"])

        # compat
        self.cpp_info.components["crashpad_compat"].set_property("cmake_target_name", "crashpad::compat")
        self.cpp_info.components["crashpad_compat"].includedirs.append(os.path.join("include", "crashpad"))
        # On Apple crashpad_compat is an interface library
        if not is_apple_os(self):
            self.cpp_info.components["crashpad_compat"].libs = ["crashpad_compat"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["crashpad_compat"].system_libs.append("dl")

        # util
        self.cpp_info.components["crashpad_util"].set_property("cmake_target_name", "crashpad::util")
        self.cpp_info.components["crashpad_util"].libs = ["crashpad_util"]
        self.cpp_info.components["crashpad_util"].requires = ["crashpad_compat", "crashpad_mini_chromium", "zlib::zlib"]
        # crashpad_util uses the vendored mpack (MessagePack) library since 0.7.
        self.cpp_info.components["crashpad_mpack"].set_property("cmake_target_name", "crashpad::mpack")
        self.cpp_info.components["crashpad_mpack"].libs = ["crashpad_mpack"]
        self.cpp_info.components["crashpad_util"].requires.append("crashpad_mpack")
        # client/settings.h declares different private members when this is 0. Crashpad
        # sets it with add_compile_definitions() for its own build only (1 except Android).
        flock = "0" if self.settings.os == "Android" else "1"
        self.cpp_info.components["crashpad_util"].defines.append(f"CRASHPAD_FLOCK_ALWAYS_SUPPORTED={flock}")
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["crashpad_util"].system_libs.extend(["pthread", "rt"])
            # Requires libcurl https://github.com/getsentry/crashpad/blob/2237d97ee2c38c930c07001e660be57324f69a37/util/CMakeLists.txt#L256
            self.cpp_info.components["crashpad_util"].requires.extend(["libcurl::libcurl"])
        elif self.settings.os == "Windows":
            self.cpp_info.components["crashpad_util"].system_libs.append("winhttp")
        elif self.settings.os == "Macos":
            self.cpp_info.components["crashpad_util"].frameworks.extend(["CoreFoundation", "Foundation", "IOKit"])
            self.cpp_info.components["crashpad_util"].system_libs.append("bsm")
        if self.options.get_safe("with_tls") == "openssl":
            self.cpp_info.components["crashpad_util"].requires.append("openssl::openssl")

        # client
        self.cpp_info.components["crashpad_client"].set_property("cmake_target_name", "crashpad::client")
        self.cpp_info.components["crashpad_client"].libs = ["crashpad_client"]
        self.cpp_info.components["crashpad_client"].requires = ["crashpad_util", "crashpad_mini_chromium"]

        # snapshot
        self.cpp_info.components["crashpad_snapshot"].set_property("cmake_target_name", "crashpad::snapshot")
        self.cpp_info.components["crashpad_snapshot"].libs = ["crashpad_snapshot"]
        self.cpp_info.components["crashpad_snapshot"].requires = [
            "crashpad_client", "crashpad_compat",
            "crashpad_util", "crashpad_mini_chromium",
        ]
        if self.settings.os == "Windows":
            self.cpp_info.components["crashpad_snapshot"].system_libs.append("powrprof")

        # minidump
        self.cpp_info.components["crashpad_minidump"].set_property("cmake_target_name", "crashpad::minidump")
        self.cpp_info.components["crashpad_minidump"].libs = ["crashpad_minidump"]
        self.cpp_info.components["crashpad_minidump"].requires = [
            "crashpad_compat", "crashpad_snapshot",
            "crashpad_util", "crashpad_mini_chromium",
        ]

        if self.settings.os == "Windows":
            # getopt
            self.cpp_info.components["crashpad_getopt"].set_property("cmake_target_name", "crashpad::getopt")
            self.cpp_info.components["crashpad_getopt"].libs = ["crashpad_getopt"]

        # handler
        self.cpp_info.components["crashpad_handler"].set_property("cmake_target_name", "crashpad::handler")
        self.cpp_info.components["crashpad_handler"].libs = ["crashpad_handler_lib"]
        self.cpp_info.components["crashpad_handler"].requires = [
            "crashpad_compat", "crashpad_minidump", "crashpad_snapshot",
            "crashpad_util", "crashpad_mini_chromium",
        ]
        if self.settings.os == "Windows":
            self.cpp_info.components["crashpad_handler"].requires.append("crashpad_getopt")

        # tools
        self.cpp_info.components["crashpad_tools"].set_property("cmake_target_name", "crashpad::tools")
        self.cpp_info.components["crashpad_tools"].libs = ["crashpad_tools"]
