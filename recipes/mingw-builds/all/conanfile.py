import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, download, rmdir


required_conan_version = ">=1.47.0"

class MingwConan(ConanFile):
    name = "mingw-builds"
    description = "MinGW is a contraction of Minimalist GNU for Windows"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/niXman/mingw-builds"
    license = "ZPL-2.1", "MIT", "GPL-2.0-or-later"
    topics = ("gcc", "gnu", "unix", "mingw32", "binutils")
    settings = "os", "arch"
    options = {"threads": ["posix", "win32"], "exception": ["seh", "sjlj"]}
    default_options = {"threads": "posix", "exception": "seh"}
    provides = "mingw-w64"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def validate(self):
        valid_os = ["Windows"]
        if str(self.settings.os) not in valid_os:
            raise ConanInvalidConfiguration(f"MinGW {self.version} is only supported for the following operating systems: {valid_os}")
        valid_arch = ["x86_64"]
        if str(self.settings.arch) not in valid_arch:
            raise ConanInvalidConfiguration(f"MinGW {self.version} is only supported for the following architectures on {self.settings.os}: {valid_arch}")

        if getattr(self, "settings_target", None):
            if str(self.settings_target.os) not in valid_os:
                raise ConanInvalidConfiguration(f"MinGW {self.version} is only supported for the following operating systems: {valid_os}")
            valid_arch = ["x86_64"]
            if str(self.settings_target.arch) not in valid_arch:
                raise ConanInvalidConfiguration(f"MinGW {self.version} is only supported for the following architectures on {self.settings.os}: {valid_arch}")
            if self.settings_target.compiler != "gcc":
                self.output.warning("Only GCC is allowed as compiler. Make sure you are using the right compiler with this package!")
            threads_value = self.settings_target.compiler.get_safe("threads")
            if str(threads_value) != str(self.options.threads):
                self.output.warning("Tool require 'mingw-builds' provides binaries for gcc "
                                 f"with options.threads={self.options.threads}, but your profile:host declares "
                                 f"settings.compiler.threads={threads_value}, please use the same value for both.")
            exception_value = self.settings_target.compiler.get_safe("exception")
            if str(exception_value) != str(self.options.exception):
                self.output.warning("Tool require 'mingw-builds' provides binaries for gcc "
                                 f"with options.exception={self.options.exception}, your profile:host declares "
                                 f"settings.compiler.exception={exception_value}, please use the same value for both.")

    def build_requirements(self):
        self.build_requires("7zip/19.00")

    def build(self):
        # Source should be downloaded in the build step since it depends on specific options
        url = self.conan_data["sources"][self.version][str(self.options.threads)][str(self.options.exception)]
        self.output.info(f"Downloading: {url['url']}")
        download(self, url["url"], "file.7z", sha256=url["sha256"])
        self.run("7z x file.7z")
        os.remove('file.7z')


    def package(self):
        target = "mingw64" if self.settings.arch == "x86_64" else "mingw32"
        copy(self, "*", src=target, dst=self.package_folder)
        rmdir(self, target)
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "opt", "lib", "cmake"))

    def package_info(self):
        if getattr(self, "settings_target", None):
            if self.settings_target.compiler != "gcc":
                self.output.warning("Only GCC is allowed as compiler. Make sure you are using the right compiler with this package!")
            threads_value = self.settings_target.compiler.get_safe("threads")
            if str(threads_value) != str(self.options.threads):
                self.output.warning("Tool require 'mingw-builds' provides binaries for gcc "
                                 f"with options.threads={self.options.threads}, but your profile:host declares "
                                 f"settings.compiler.threads={threads_value}, please use the same value for both.")
            exception_value = self.settings_target.compiler.get_safe("exception")
            if str(exception_value) != str(self.options.exception):
                self.output.warning("Tool require 'mingw-builds' provides binaries for gcc "
                                 f"with options.exception={self.options.exception}, your profile:host declares "
                                 f"settings.compiler.exception={exception_value}, please use the same value for both.")

        self.buildenv_info.define("MINGW_HOME", str(self.package_folder))
        self.buildenv_info.define("CONAN_CMAKE_GENERATOR", "MinGW Makefiles")
        self.buildenv_info.define("CXX", os.path.join(self.package_folder, "bin", "g++.exe").replace("\\", "/"))
        self.buildenv_info.define("CC", os.path.join(self.package_folder, "bin", "gcc.exe").replace("\\", "/"))
        self.buildenv_info.define("LD", os.path.join(self.package_folder, "bin", "ld.exe").replace("\\", "/"))
        self.buildenv_info.define("NM", os.path.join(self.package_folder, "bin", "nm.exe").replace("\\", "/"))
        self.buildenv_info.define("AR", os.path.join(self.package_folder, "bin", "ar.exe").replace("\\", "/"))
        self.buildenv_info.define("AS", os.path.join(self.package_folder, "bin", "as.exe").replace("\\", "/"))
        self.buildenv_info.define("STRIP", os.path.join(self.package_folder, "bin", "strip.exe").replace("\\", "/"))
        self.buildenv_info.define("RANLIB", os.path.join(self.package_folder, "bin", "ranlib.exe").replace("\\", "/"))
        self.buildenv_info.define("STRINGS", os.path.join(self.package_folder, "bin", "strings.exe").replace("\\", "/"))
        self.buildenv_info.define("OBJDUMP", os.path.join(self.package_folder, "bin", "objdump.exe").replace("\\", "/"))
        self.buildenv_info.define("GCOV", os.path.join(self.package_folder, "bin", "gcov.exe").replace("\\", "/"))

        # TODO: Remove this after conan v1 support is dropped
        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)
        self.env_info.MINGW_HOME = str(self.package_folder)

        self.env_info.CONAN_CMAKE_GENERATOR = "MinGW Makefiles"
        self.env_info.CXX = os.path.join(self.package_folder, "bin", "g++.exe").replace("\\", "/")
        self.env_info.CC = os.path.join(self.package_folder, "bin", "gcc.exe").replace("\\", "/")
        self.env_info.LD = os.path.join(self.package_folder, "bin", "ld.exe").replace("\\", "/")
        self.env_info.NM = os.path.join(self.package_folder, "bin", "nm.exe").replace("\\", "/")
        self.env_info.AR = os.path.join(self.package_folder, "bin", "ar.exe").replace("\\", "/")
        self.env_info.AS = os.path.join(self.package_folder, "bin", "as.exe").replace("\\", "/")
        self.env_info.STRIP = os.path.join(self.package_folder, "bin", "strip.exe").replace("\\", "/")
        self.env_info.RANLIB = os.path.join(self.package_folder, "bin", "ranlib.exe").replace("\\", "/")
        self.env_info.STRINGS = os.path.join(self.package_folder, "bin", "strings.exe").replace("\\", "/")
        self.env_info.OBJDUMP = os.path.join(self.package_folder, "bin", "objdump.exe").replace("\\", "/")
        self.env_info.GCOV = os.path.join(self.package_folder, "bin", "gcov.exe").replace("\\", "/")
