from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob

required_conan_version = ">=1.33.0"


class ArmToolchainConan(ConanFile):
    name = "arm-toolchain"
    homepage = "https://developer.arm.com/"
    description = "The GNU Toolchain for the Cortex-A Family is a ready-to-use, open source suite of tools for C, C++ and Assembly programming."
    url = "https://github.com/conan-io/conan-center-index"
    license = ("GPL-3-or-later",)
    topics = ("arm", "gcc", "binutils", "toolchain")
    options = {
        "target_arch": ["armv8", "armv7hf"],
        "target_os": ["Linux", ],
    }
    default_options = {
        "target_arch": "armv8",
        "target_os": "Linux",
    }
    settings = "os", "arch", "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _sources_dict(self):
        try:
            return self.conan_data["sources"][self.version][self._target_arch][self._target_os][str(self.settings.os)]
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
        self.build_requires("tar/1.32.90")

    def validate(self):
        if hasattr(self, "settings_target"):
            if (self.options.target_arch, self.options.target_os) != (str(self.settings_target.arch), str(self.settings_target.os)):
                raise ConanInvalidConfiguration("arm-toolchain:{target_arch={} target_os={}} does not match settings_target.{arch={} os={}}".format(
                    self.options.target_arch, self.options.target_os, self.settings_target.arch, self.settings_target.os))

        if self._sources_dict is None:
            raise ConanInvalidConfiguration("No arm toolchain available for this system or profile does not support it yet.")

    @property
    def _target_arch(self):
        return str(self.options.target_arch)

    @property
    def _target_os(self):
        return str(self.options.target_os)

    def build(self):
        # FIXME: downloads.arm.com returns 403 (https://github.com/conan-io/conan/issues/9036)
        # FIXME: tools.get cannot extract the tarball (KeyError: "linkname 'gcc-arm-10.3-2021.07-x86_64-aarch64-none-linux-gnu/aarch64-none-linux-gnu/libc/usr/bin/getconf' not found")
        tools.get(**self._sources_dict, filename="archive.tar.gz", destination=self._source_subfolder, strip_root=True)
        tools.download(**self._sources_dict, filename="archive.tar.gz",
                       headers={"User-Agent": "conan client"})

        self.run("tar xf archive.tar.gz", run_environment=True)
        os.unlink("archive.tar.gz")
        tools.rename(glob.glob("gcc-*")[0], self._source_subfolder)

    def package(self):
        self.copy("*", src=self._source_subfolder, dst=self.package_folder)
        for fn in glob.glob(os.path.join(self.package_folder, "*.txt")):
            os.unlink(fn)

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.path.append(bin_path)

        target_gnu_arch = {
            "armv8": "aarch64",
            "armv7hf": "arm",
        }[self._target_arch]
        target_gnu_os = {
            "Linux": "linux",
        }[self._target_os]
        target_gnu_abi = {
            "armv8": "gnu",
            "armv7hf": "gnueabihf",
        }[self._target_arch]
        prefix = "{}-none-{}-{}-".format(target_gnu_arch, target_gnu_os, target_gnu_abi)

        cmake_system_os = {
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
