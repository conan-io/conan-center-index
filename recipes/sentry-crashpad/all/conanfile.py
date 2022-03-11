import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.28.0"


class SentryCrashpadConan(ConanFile):
    name = "sentry-crashpad"
    description = "Crashpad is a crash-reporting system."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/getsentry/sentry-native"
    license = "Apache-2.0"
    topics = ("conan", "crashpad", "error-reporting", "crash-reporting")
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
    exports_sources = "CMakeLists.txt", "patches/*"
    generators = "cmake"
    short_paths = True

    _cmake = None

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ("Linux", "Android") or tools.Version(self.version) < "0.4":
            del self.options.with_tls

    def requirements(self):
        self.requires("zlib/1.2.11")
        if self.options.get_safe("with_tls"):
            self.requires("openssl/1.1.1l")

    def validate(self):
        if self.settings.compiler.cppstd:
            # Set as required in crashpad CMake file.
            # See https://github.com/getsentry/crashpad/blob/71bcaad4cf30294b8de1bfa02064ab629437163b/CMakeLists.txt#L67
            tools.check_min_cppstd(self, 14)

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("Compiler is unknown. Assuming it supports C++14.")
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("Build requires support for C++14. Minimum version for {} is {}"
                .format(str(self.settings.compiler), minimum_version))
        if tools.Version(self.version) < "0.4.7" and self.settings.os == "Macos" and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration("This version doesn't support ARM compilation")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CRASHPAD_ENABLE_INSTALL"] = True
        self._cmake.definitions["CRASHPAD_ENABLE_INSTALL_DEV"] = True
        self._cmake.definitions["CRASHPAD_ZLIB_SYSTEM"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if tools.Version(self.version) > "0.4":
            openssl_repl = "find_package(OpenSSL REQUIRED)" if self.options.get_safe("with_tls") else ""
            tools.replace_in_file(os.path.join(self._source_subfolder, "external", "crashpad", "CMakeLists.txt"),
                                  "find_package(OpenSSL)", openssl_repl)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=os.path.join(self._source_subfolder, "external", "crashpad"))
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "crashpad"
        self.cpp_info.names["cmake_find_package_multi"] = "crashpad"
        self.cpp_info.filenames["cmake_find_package"] = "crashpad"
        self.cpp_info.filenames["cmake_find_package_multi"] = "crashpad"

        self.cpp_info.components["mini_chromium"].includedirs.append(os.path.join("include", "crashpad", "mini_chromium"))
        self.cpp_info.components["mini_chromium"].libs = ["mini_chromium"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["mini_chromium"].system_libs.append("pthread")
        if tools.is_apple_os(self.settings.os):
            if self.settings.os == "Macos":
                self.cpp_info.components["mini_chromium"].frameworks = ["ApplicationServices", "CoreFoundation", "Foundation", "IOKit", "Security"]
            else:  # iOS
                self.cpp_info.components["mini_chromium"].frameworks = ["CoreFoundation", "CoreGraphics", "CoreText", "Foundation", "Security"]

        self.cpp_info.components["compat"].includedirs.append(os.path.join("include", "crashpad"))
        # On Apple crashpad_compat is an interface library
        if not tools.is_apple_os(self.settings.os):
            self.cpp_info.components["compat"].libs = ["crashpad_compat"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["compat"].system_libs.append("dl")

        self.cpp_info.components["util"].libs = ["crashpad_util"]
        self.cpp_info.components["util"].requires = ["compat", "mini_chromium", "zlib::zlib"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["util"].system_libs.extend(["pthread", "rt"])
        elif self.settings.os == "Windows":
            self.cpp_info.components["util"].system_libs.append("winhttp")
        if self.options.get_safe("with_tls") == "openssl":
            self.cpp_info.components["util"].requires.append("openssl::openssl")

        if self.settings.os == "Macos":
            self.cpp_info.components["util"].frameworks.extend(["CoreFoundation", "Foundation", "IOKit"])
            self.cpp_info.components["util"].system_libs.append("bsm")

        self.cpp_info.components["client"].libs = ["crashpad_client"]
        self.cpp_info.components["client"].requires = ["util", "mini_chromium"]

        self.cpp_info.components["snapshot"].libs = ["crashpad_snapshot"]
        self.cpp_info.components["snapshot"].requires = ["client", "compat", "util", "mini_chromium"]
        if self.settings.os == "Windows":
            self.cpp_info.components["snapshot"].system_libs.append("powrprof")

        self.cpp_info.components["minidump"].libs = ["crashpad_minidump"]
        self.cpp_info.components["minidump"].requires = ["compat", "snapshot", "util", "mini_chromium"]

        if tools.Version(self.version) > "0.3":
            if self.settings.os == "Windows":
                self.cpp_info.components["getopt"].libs = ["crashpad_getopt"]

            self.cpp_info.components["handler"].libs = ["crashpad_handler_lib"]
            self.cpp_info.components["handler"].requires = ["compat", "minidump", "snapshot", "util", "mini_chromium"]
            if self.settings.os == "Windows":
                self.cpp_info.components["handler"].requires.append("getopt")

        self.cpp_info.components["tools"].libs = ["crashpad_tools"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
