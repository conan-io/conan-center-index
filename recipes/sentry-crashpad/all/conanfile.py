import os

from conan import ConanFile
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, apply_conandata_patches, copy, rmdir, rm, replace_in_file
from conan.tools.apple.apple import is_apple_os
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.43.0"


class SentryCrashpadConan(ConanFile):
    name = "sentry-crashpad"
    description = "Crashpad is a crash-reporting system."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/getsentry/sentry-native"
    license = "Apache-2.0"
    topics = ("crashpad", "error-reporting", "crash-reporting")

    provides = "crashpad", "mini_chromium"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_tls": ["openssl", False],
    }
    default_options = {
        "fPIC": True,
        "with_tls": "openssl",
    }

    short_paths = True

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15" if Version(self.version) < "0.4.16" else "16",
            "gcc": "6",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, patch["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ("Linux", "Android") or Version(self.version) < "0.4":
            del self.options.with_tls

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CRASHPAD_ENABLE_INSTALL"] = True
        tc.variables["CRASHPAD_ENABLE_INSTALL_DEV"] = True
        tc.variables["CRASHPAD_ZLIB_SYSTEM"] = True
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def layout(self):
        cmake_layout(self)

    def build_requirements(self):
        if self._is_mingw:
            self.build_requires("jwasm/2.13")

    def requirements(self):
        self.requires("zlib/1.2.12")
        if self.options.get_safe("with_tls"):
            self.requires("openssl/1.1.1n")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            # Set as required in crashpad CMake file.
            # See https://github.com/getsentry/crashpad/blob/71bcaad4cf30294b8de1bfa02064ab629437163b/CMakeLists.txt#L67
            tools.check_min_cppstd(self, 14)

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("Compiler is unknown. Assuming it supports C++14.")
        elif Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("Build requires support for C++14. Minimum version for {} is {}"
                .format(str(self.settings.compiler), minimum_version))
        if Version(self.version) < "0.4.7" and self.settings.os == "Macos" and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration("This version doesn't support ARM compilation")

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)])

    def build(self):
        apply_conandata_patches(self)
        if Version(self.version) > "0.4":
            openssl_repl = "find_package(OpenSSL REQUIRED)" if self.options.get_safe("with_tls") else ""
            replace_in_file(self, os.path.join(self.source_folder, "external", "crashpad", "CMakeLists.txt"),
                                  "find_package(OpenSSL)", openssl_repl)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.build_folder, os.path.join(self.package_folder, "licenses"))
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
        elif is_apple_os(self.settings.os):
            self.cpp_info.components["crashpad_mini_chromium"].frameworks = ["CoreFoundation", "Foundation", "Security"]
            if self.settings.os == "Macos":
                self.cpp_info.components["crashpad_mini_chromium"].frameworks.extend(["ApplicationServices", "IOKit"])
            else:  # iOS
                self.cpp_info.components["crashpad_mini_chromium"].frameworks.extend(["CoreGraphics", "CoreText"])

        # compat
        self.cpp_info.components["crashpad_compat"].set_property("cmake_target_name", "crashpad::compat")
        self.cpp_info.components["crashpad_compat"].includedirs.append(os.path.join("include", "crashpad"))
        # On Apple crashpad_compat is an interface library
        if not is_apple_os(self.settings.os):
            self.cpp_info.components["crashpad_compat"].libs = ["crashpad_compat"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["crashpad_compat"].system_libs.append("dl")

        # util
        self.cpp_info.components["crashpad_util"].set_property("cmake_target_name", "crashpad::util")
        self.cpp_info.components["crashpad_util"].libs = ["crashpad_util"]
        self.cpp_info.components["crashpad_util"].requires = ["crashpad_compat", "crashpad_mini_chromium", "zlib::zlib"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["crashpad_util"].system_libs.extend(["pthread", "rt"])
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
            self.cpp_info.components["snapshot"].system_libs.append("powrprof")

        # minidump
        self.cpp_info.components["crashpad_minidump"].set_property("cmake_target_name", "crashpad::minidump")
        self.cpp_info.components["crashpad_minidump"].libs = ["crashpad_minidump"]
        self.cpp_info.components["crashpad_minidump"].requires = [
            "crashpad_compat", "crashpad_snapshot",
            "crashpad_util", "crashpad_mini_chromium",
        ]

        if Version(self.version) > "0.3":
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

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
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
        if Version(self.version) > "0.3":
            if self.settings.os == "Windows":
                self.cpp_info.components["crashpad_getopt"].names["cmake_find_package"] = "getopt"
                self.cpp_info.components["crashpad_getopt"].names["cmake_find_package_multi"] = "getopt"
            self.cpp_info.components["crashpad_handler"].names["cmake_find_package"] = "handler"
            self.cpp_info.components["crashpad_handler"].names["cmake_find_package_multi"] = "handler"
        self.cpp_info.components["crashpad_tools"].names["cmake_find_package"] = "tools"
        self.cpp_info.components["crashpad_tools"].names["cmake_find_package_multi"] = "tools"
