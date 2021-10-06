from conans import ConanFile, tools
from conans import __version__ as conan_version
from conans.errors import ConanInvalidConfiguration
import os
import glob

required_conan_version = ">=1.33.0"


class ArmToolchainConan(ConanFile):
    name = "arm-toolchain"
    homepage = "https://developer.arm.com/"
    description = "The GNU Toolchain for the Cortex-A Family is a ready-to-use, open source suite of tools for C, C++ and Assembly programming."
    url = "https://github.com/conan-io/conan-center-index"
    license = ("GPL-3-or-later", "GPL-2-or-later", "LPGL-2.1-or-later", "MIT", "ZLIB", "BSD-3-Clause", "EULA")
    topics = ("arm", "gcc", "binutils", "toolchain")
    options = {
        "target_arch": ["armv8", "armv7hf", "armv7"],
        "target_os": ["Arduino", "Linux", ],
    }
    default_options = {
        "target_arch": "armv8",
        "target_os": "Linux",
    }
    settings = "os", "arch"

    exports_sources = "patches/*"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _sources_dict(self):
        arch = self.settings.arch
        if (self.settings.os, self.settings.arch) == ("Windows", "x86_64"):
            arch = "x86"
        try:
            return self.conan_data["sources"][self.version][self._target_arch][self._target_os][str(arch)][str(self.settings.os)]
        except KeyError:
            return None

    def config_options(self):
        if hasattr(self, "settings_target"):
            self.options.target_arch = str(self.settings_target.arch)
            self.options.target_os = str(self.settings_target.os)
        else:
            self.options.target_arch = "armv8"
            self.options.target_os = "Linux"

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.build_requires("msys2/cci.latest")
        else:
            self.build_requires("tar/1.32.90")

    def validate(self):
        if hasattr(self, "settings_target"):
            if (self.options.target_arch, self.options.target_os) != (str(self.settings_target.arch), str(self.settings_target.os)):
                raise ConanInvalidConfiguration("arm-toolchain:{target_arch={} target_os={}} does not match settings_target.{arch={} os={}}".format(
                    self.options.target_arch, self.options.target_os, self.settings_target.arch, self.settings_target.os, "gcc"))
            if self.settings_target.compiler != "gcc":
                raise ConanInvalidConfiguration("arm-toolchain only provides a gcc compiler")

        if self._sources_dict is None:
            raise ConanInvalidConfiguration("No arm toolchain available for this host/target system combination.")

    @property
    def _target_arch(self):
        return str(self.options.target_arch)

    @property
    def _target_os(self):
        return str(self.options.target_os)

    def build(self):
        # FIXME: downloads.arm.com returns 403 (https://github.com/conan-io/conan/issues/9036)
        # FIXME: tools.get cannot extract the tarball (KeyError: "linkname 'gcc-arm-10.3-2021.07-x86_64-aarch64-none-linux-gnu/aarch64-none-linux-gnu/libc/usr/bin/getconf' not found")
        tools.download(**self._sources_dict, filename="archive.tar.xz",
                       headers={"User-Agent": "Conan v{}".format(conan_version)})

        self.run("tar xf archive.tar.xz", run_environment=True, win_bash=self._settings_build.os == "Windows")
        os.unlink("archive.tar.xz")
        tools.rename(glob.glob("gcc-*")[0], self._source_subfolder)

        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def package(self):
        self.copy("EULA", src=self._source_subfolder, dst="licenses")
        self.copy("*", src=self._source_subfolder, dst=os.path.join(self.package_folder, "bin"))
        for fn in glob.glob(os.path.join(self.package_folder, "*.txt")):
            os.unlink(fn)

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin", "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.path.append(bin_path)

        target_gnu_arch = {
            "armv8": "aarch64",
            "armv7": "arm",
            "armv7hf": "arm",
        }[self._target_arch]
        target_gnu_os = "none" + {
            "Arduino": "",
            "Linux": "-linux",
        }[self._target_os]
        target_gnu_abi = {
            ("armv8", "Arduino"): "elf",
            ("armv8", "Linux"): "gnu",
            ("armv7", "Arduino"): "eabi",
            ("armv7hf", "Linux"): "gnueabihf",
        }[(self._target_arch, self._target_os)]
        prefix = "{}-{}-{}-".format(target_gnu_arch, target_gnu_os, target_gnu_abi)

        cmake_system_os = {
            "Arduino": "Generic",
            "Linux": "Linux",
        }[self._target_os]

        self.user_info.target_gnu_arch = target_gnu_arch
        self.user_info.target_gnu_os = target_gnu_os
        self.user_info.target_gnu_abi = target_gnu_abi
        self.user_info.cmake_system_os = cmake_system_os

        self.env_info.CC = prefix + "gcc"
        self.env_info.CXX = prefix + "g++"
        self.env_info.CPP = prefix + "cpp"
        self.env_info.AR = prefix + "ar"
        self.env_info.AS = prefix + "as"
        self.env_info.GDB = prefix + "gdb"
        self.env_info.NM = prefix + "nm"
        self.env_info.OBJCOPY = prefix + "objcopy"
        self.env_info.OBJDUMP = prefix + "objdump"
        self.env_info.RANLIB = prefix + "ranlib"
        self.env_info.SIZE = prefix + "size"
        self.env_info.STRINGS = prefix + "strings"
        self.env_info.STRIP = prefix + "strip"
