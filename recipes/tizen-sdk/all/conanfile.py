from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class TizenSDKConan(ConanFile):
    name = "tizen-sdk"
    description = "The Tizen SDK is a toolset that lets you compile code for Tizen platform, using languages such as C and C++"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://docs.tizen.org/application/"
    topics = ("tizen", "sdk", "toolchain", "compiler")
    license = "Apache-2.0"

    settings = "os", "arch", "build_type", "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _arch(self):
        return self.settings.arch

    @property
    def _triplet(self):
        arch = {
            "armv8": "aarch64",
        }.get(str(self.settings_target.arch))

        return f"{arch}-linux-gnu"

    @property
    def _sdk_version_major(self):
        version_data = self.version.split("_")
        return version_data[0]

    @property
    def _sdk_version_minor(self):
        version_data = self.version.split("_")
        return version_data[1]

    @property
    def _sdk_root(self):
        return os.path.join(self.package_folder)

    @property
    def _tizen_abi(self):
        return {
            "armv7": "arm",
            "armv8": "aarch64",
            "x86": "i586",
            "x86_64": "x86_64",
        }.get(str(self.settings_target.arch))

    def _wrap_executable(self, tool):
        suffix = ".exe" if self.settings.os == "Windows" else ""
        return f"{tool}{suffix}"

    def _tool_name(self, tool):
        prefix = f"{self._triplet}"
        executable = f"{prefix}-{tool}"
        return self._wrap_executable(executable)

    def _define_tool_var(self, name, value):
        sdk_bin = os.path.join(self._sdk_root, "bin")
        path = os.path.join(sdk_bin, self._tool_name(value))

        if not os.path.isfile(path):
            self.output.error(f"'Environment variable {name} could not be created: '{path}'")
            return "UNKNOWN"

        self._chmod_plus_x(path)
        self.output.info(f"Creating {name} environment variable: {path}")
        return path

    def build(self):
        tools.get(**self.conan_data["sources"][self.version][str(self.settings.os)][str(self._arch)], destination=self._source_subfolder)

    def package(self):
        version = self._sdk_version_major
        abi = self._tizen_abi
        self.copy("*", src=os.path.join(self._source_subfolder, "data", "tools", f"{abi}-linux-gnu-gcc-{version}"), dst=".", keep_path=True, symlinks=True)
        #self._fix_permissions()

    def validate(self):
        if not self._settings_os_supported():
            raise ConanInvalidConfiguration(f"os={self.settings.os} is not supported by {self.name} (no binaries are available)")
        if not self._settings_arch_supported():
            raise ConanInvalidConfiguration(f"os,arch={self.settings.os},{self.settings.arch} is not supported by {self.name} (no binaries are available)")

    def package_info(self):
        self.output.info(f"Creating TIZEN_SDK_ROOT environment variable: {self._sdk_root}")
        self.env_info.TIZEN_SDK_ROOT = self._sdk_root

        # we need this?
        self.output.info(f"Creating CHOST environment variable: {self._triplet}")
        self.env_info.CHOST = self._triplet

        sdk_sysroot = os.path.join(self._sdk_root)
        self.output.info(f"Creating CONAN_CMAKE_FIND_ROOT_PATH environment variable: {sdk_sysroot}")
        self.env_info.CONAN_CMAKE_FIND_ROOT_PATH = sdk_sysroot

        self.output.info(f"Creating SYSROOT environment variable: {sdk_sysroot}")
        self.env_info.SYSROOT = sdk_sysroot

        self.output.info(f"Creating self.cpp_info.sysroot: {sdk_sysroot}")
        self.cpp_info.sysroot = sdk_sysroot

        self.env_info.CC = self._define_tool_var("CC", "gcc")
        self.env_info.CXX = self._define_tool_var("CXX", "g++")
        self.env_info.AR = self._define_tool_var("AR", "ar")
        self.env_info.AS = self._define_tool_var("AS", "as")
        self.env_info.RANLIB = self._define_tool_var("RANLIB", "ranlib")
        self.env_info.STRIP = self._define_tool_var("STRIP", "strip")
        self.env_info.ADDR2LINE = self._define_tool_var("ADDR2LINE", "addr2line")
        self.env_info.NM = self._define_tool_var("NM", "nm")
        self.env_info.OBJCOPY = self._define_tool_var("OBJCOPY", "objcopy")
        self.env_info.OBJDUMP = self._define_tool_var("OBJDUMP", "objdump")
        self.env_info.READELF = self._define_tool_var("READELF", "readelf")
        self.env_info.LD = self._define_tool_var("LD", "ld")

        self.env_info.CMAKE_SYSTEM_NAME = "Linux"
        self.env_info.CMAKE_C_COMPILER_TARGET = self._triplet
        self.env_info.CMAKE_CXX_COMPILER_TARGET = self._triplet
        self.env_info.CMAKE_CROSSCOMPILING = 1

        self.env_info.CMAKE_FIND_ROOT_PATH_MODE_PROGRAM = "NEVER"
        self.env_info.CMAKE_FIND_ROOT_PATH_MODE_LIBRARY = "ONLY"
        self.env_info.CMAKE_FIND_ROOT_PATH_MODE_INCLUDE = "ONLY"
        self.env_info.CMAKE_FIND_ROOT_PATH_MODE_PACKAGE = "ONLY"

    def _settings_os_supported(self):
        return self.conan_data["sources"][self.version].get(str(self.settings.os)) is not None

    def _settings_arch_supported(self):
        return self.conan_data["sources"][self.version].get(str(self.settings.os), {}).get(str(self._arch)) is not None

    def _fix_permissions(self):
        if os.name != "posix":
            return
        for root, _, files in os.walk(self.package_folder):
            for filename in files:
                filename = os.path.join(root, filename)
                with open(filename, "rb") as f:
                    sig = f.read(4)
                    if type(sig) is str:
                        sig = [ord(s) for s in sig]
                    else:
                        sig = [s for s in sig]
                    if len(sig) > 2 and sig[0] == 0x23 and sig[1] == 0x21:
                        self.output.info(f"chmod on script file: '{filename}'")
                        self._chmod_plus_x(filename)
                    elif sig == [0x7F, 0x45, 0x4C, 0x46]:
                        self.output.info(f"chmod on ELF file: '{filename}'")
                        self._chmod_plus_x(filename)
                    elif sig == [0xCA, 0xFE, 0xBA, 0xBE] or \
                         sig == [0xBE, 0xBA, 0xFE, 0xCA] or \
                         sig == [0xFE, 0xED, 0xFA, 0xCF] or \
                         sig == [0xCF, 0xFA, 0xED, 0xFE] or \
                         sig == [0xFE, 0xEF, 0xFA, 0xCE] or \
                         sig == [0xCE, 0xFA, 0xED, 0xFE]:
                        self.output.info(f"chmod on Mach-O file: '{filename}'")
                        self._chmod_plus_x(filename)

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == "posix":
            os.chmod(filename, os.stat(filename).st_mode | 0o111)
