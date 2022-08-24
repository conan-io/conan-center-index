from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import functools
import os
import re
import typing
import unittest


required_conan_version = ">=1.43.0"


# This recipe includes a selftest to test conversion of os/arch to triplets (and vice verse)
# Run it using `python -m unittest conanfile.py`


class BinutilsConan(ConanFile):
    name = "binutils"
    description = "The GNU Binutils are a collection of binary tools."
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index/"
    homepage = "https://www.gnu.org/software/binutils"
    topics = ("binutils", "ld", "linker", "as", "assembler", "objcopy", "objdump")
    settings = "os", "arch", "compiler", "build_type"

    _PLACEHOLDER_TEXT = "__PLACEHOLDER__"

    options = {
        "multilib": [True, False],
        "with_libquadmath": [True, False],
        "target_arch": "ANY",
        "target_os": "ANY",
        "target_triplet": "ANY",
        "prefix": "ANY",
    }

    default_options = {
        "multilib": True,
        "with_libquadmath": True,
        "target_arch": _PLACEHOLDER_TEXT,  # Initialized in configure, checked in validate
        "target_os": _PLACEHOLDER_TEXT,  # Initialized in configure, checked in validate
        "target_triplet": _PLACEHOLDER_TEXT,  # Initialized in configure, checked in validate
        "prefix": _PLACEHOLDER_TEXT,  # Initialized in configure (NOT config_options, because it depends on target_{arch,os})
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _settings_target(self):
        return getattr(self, "settings_target", None) or self.settings

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def configure(self):
        if self.options.target_triplet == self._PLACEHOLDER_TEXT:
            if self.options.target_arch == self._PLACEHOLDER_TEXT:
                # If target triplet and target arch are not set, initialize it from the target settings
                self.options.target_arch = str(self._settings_target.arch)
            if self.options.target_os == self._PLACEHOLDER_TEXT:
                # If target triplet and target os are not set, initialize it from the target settings
                self.options.target_os = str(self._settings_target.os)
            # Initialize the target_triplet from the target arch and target os
            self.options.target_triplet = _GNUTriplet.from_archos(_ArchOs(arch=str(self.options.target_arch), os=str(self.options.target_os), extra=dict(self._settings_target.values_list))).triplet
        else:
            gnu_triplet_obj = _GNUTriplet.from_text(str(self.options.target_triplet))
            archos = _ArchOs.from_triplet(gnu_triplet_obj)
            if self.options.target_arch == self._PLACEHOLDER_TEXT:
                # If target arch is not set, deduce it from the target triplet
                self.options.target_arch = archos.arch
            if self.options.target_os == self._PLACEHOLDER_TEXT:
                # If target arch is not set, deduce it from the target triplet
                self.options.target_os = archos.os

        if self.options.prefix == self._PLACEHOLDER_TEXT:
            self.options.prefix = f"{self.options.target_triplet}-"

        self.output.info(f"binutils:target_arch={self.options.target_arch}")
        self.output.info(f"binutils:target_os={self.options.target_os}")
        self.output.info(f"binutils:target_triplet={self.options.target_triplet}")

    def validate(self):
        if self.settings.compiler in ("msvc", "Visual Studio"):
            raise ConanInvalidConfiguration("This recipe does not support building binutils by this compiler")

        if self.options.target_os == "Macos":
            raise ConanInvalidConfiguration("cci does not support building binutils for Macos since binutils is degraded there (no as/ld + armv8 does not build)")

        # Check whether the actual target_arch and target_os option are valid (they should be in settings.yml)
        # FIXME: does there exist a stable Conan API to accomplish this?
        if self.options.target_arch not in self.settings.arch.values_range:
            raise ConanInvalidConfiguration(f"target_arch={self.options.target_arch} is invalid (possibilities={self.settings.arch.values_range})")
        if self.options.target_os not in self.settings.os.values_range:
            raise ConanInvalidConfiguration(f"target_os={self.options.target_os} is invalid (possibilities={self.settings.os.values_range})")

        target_archos = _ArchOs(str(self.options.target_arch), str(self.options.target_os))
        target_gnu_triplet = _GNUTriplet.from_text(str(self.options.target_triplet))
        if not target_archos.is_compatible(target_gnu_triplet):
            suggested_gnu_triplet = _GNUTriplet.from_archos(target_archos)
            suggested_archos = _ArchOs.from_triplet(target_gnu_triplet)
            raise ConanInvalidConfiguration(f"target_arch={target_archos.arch}/target_os={target_archos.os} is not compatible with {target_gnu_triplet.triplet}. Change target triplet to {suggested_gnu_triplet.triplet}, or change target_arch/target_os to {suggested_archos.arch}/{suggested_archos.os}.")

        # Check, when used as build requirement in a cross build, whether the target arch/os agree
        settings_target = getattr(self, "settings_target", None)
        if settings_target is not None:
            if self.options.target_arch != settings_target.arch:
                raise ConanInvalidConfiguration(f"binutils:target_arch={self.options.target_arch} does not match target architecture={settings_target.arch}")
            if self.options.target_os != settings_target.os:
                raise ConanInvalidConfiguration(f"binutils:target_os={self.options.target_os} does not match target os={settings_target.os}")

    def package_id(self):
        del self.info.settings.compiler

    def _raise_unsupported_configuration(self, key, value):
        raise ConanInvalidConfiguration(f"This configuration is unsupported by this conan recip. Please consider adding support. ({key}={value})")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def requirements(self):
        self.requires("zlib/1.2.12")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    @property
    def _exec_prefix(self):
        return os.path.join(self.package_folder, "bin", "exec_prefix")

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=self._settings_build.os == "Windows")
        yes_no = lambda tf : "yes" if tf else "no"
        conf_args = [
            f"--target={self.options.target_triplet}",
            f"--enable-multilib={yes_no(self.options.multilib)}",
            "--with-system-zlib",
            "--disable-nls",
            f"--program-prefix={self.options.prefix}",
            f"exec_prefix={tools.unix_path(self._exec_prefix)}",
        ]
        autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING*", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        target_bindir = os.path.join(self._exec_prefix, str(self.options.target_triplet), "bin")
        self.output.info("Appending PATH environment variable: {}".format(target_bindir))
        self.env_info.PATH.append(target_bindir)

        self.output.info(f"GNU triplet={self.options.target_triplet}")
        self.user_info.gnu_triplet = self.options.target_triplet

        self.output.info(f"executable prefix={self.options.prefix}")
        self.user_info.prefix = self.options.prefix

        # Add recipe path to enable running the self test in the test package.
        # Don't use this property in production code. It's unsupported.
        self.user_info.recipe_path = os.path.realpath(__file__)


class _ArchOs:
    def __init__(self, arch: str, os: str, extra: typing.Optional[typing.Dict[str, str]]=None):
        self.arch = arch
        self.os = os
        self.extra = extra if extra is not None else {}

    def is_compatible(self, triplet: "_GNUTriplet") -> bool:
        return self.arch in self.calculate_archs(triplet) and self.os == self.calculate_os(triplet)

    _MACHINE_TO_ARCH_LUT = {
        "arm": "armv7",
        "aarch64": ("armv8", "armv9"),
        "i386": "x86",
        "i486": "x86",
        "i586": "x86",
        "i686": "x86",
        "x86_64": "x86_64",
        "riscv32": "riscv32",
        "riscv64": "riscv64",
    }

    @classmethod
    def calculate_archs(cls, triplet: "_GNUTriplet") -> typing.Tuple[str]:
        if triplet.machine == "arm":
            archs = "armv7" + ("hf" if "hf" in triplet.abi else "")
        else:
            archs = cls._MACHINE_TO_ARCH_LUT[triplet.machine]
        if isinstance(archs, str):
            archs = (archs, )
        return archs

    _GNU_OS_TO_OS_LUT = {
        None: "baremetal",
        "android": "Android",
        "mingw32": "Windows",
        "linux": "Linux",
        "freebsd": "FreeBSD",
        "darwin": "Macos",
        "none": "baremetal",
        "unknown": "baremetal",
    }

    @classmethod
    def calculate_os(cls, triplet: "_GNUTriplet") -> str:
        if triplet.abi and "android" in triplet.abi:
            return "Android"
        return cls._GNU_OS_TO_OS_LUT[triplet.os]

    @classmethod
    def from_triplet(cls, triplet: "_GNUTriplet") -> "_ArchOs":
        archs = cls.calculate_archs(triplet)
        os = cls.calculate_os(triplet)
        extra = {}

        if os == "Android" and triplet.abi:
            m = re.match(".*([0-9]+)", triplet.abi)
            if m:
                extra["os.api_level"] = m.group(1)

        # Assume first architecture
        return cls(arch=archs[0], os=os, extra=extra)

    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False
        if not (self.arch == other.arch and self.os == other.os):
            return False
        self_extra_keys = set(self.extra.keys())
        other_extra_keys = set(other.extra.keys())
        if (self_extra_keys - other_extra_keys) or (other_extra_keys - self_extra_keys):
            return False
        return True

    def __repr__(self) -> str:
        return f"<{type(self).__name__}:arch='{self.arch}',os='{self.os}',extra={self.extra}>"


class _GNUTriplet:
    def __init__(self, machine: str, vendor: typing.Optional[str], os: typing.Optional[str], abi: typing.Optional[str]):
        self.machine = machine
        self.vendor = vendor
        self.os = os
        self.abi = abi

    @property
    def triplet(self) -> str:
        return "-".join(p for p in (self.machine, self.vendor, self.os, self.abi) if p)

    @classmethod
    def from_archos(cls, archos: _ArchOs) -> "_GNUTriplet":
        gnu_machine = cls.calculate_gnu_machine(archos)
        gnu_vendor = cls.calculate_gnu_vendor(archos)
        gnu_os = cls.calculate_gnu_os(archos)
        gnu_abi = cls.calculate_gnu_abi(archos)

        return cls(gnu_machine, gnu_vendor, gnu_os, gnu_abi)

    @classmethod
    def from_text(cls, text: str) -> "_GNUTriplet":
        gnu_machine: str
        gnu_vendor: typing.Optional[str]
        gnu_os: typing.Optional[str]
        gnu_abi: typing.Optional[str]

        parts = text.split("-")
        if not 2 <= len(parts) <= 4:
            raise ValueError("Wrong number of GNU triplet components. Count must lie in range [2, 4]. format=$machine(-$vendor)?(-$os)?(-$abi)?")

        gnu_machine = parts[0]
        parts = parts[1:]
        if any(v in parts[-1] for v in  cls.KNOWN_GNU_ABIS):
            gnu_abi = parts[-1]
            parts = parts[:-1]
        else:
            gnu_abi = None

        if len(parts) == 2:
            gnu_vendor = parts[0]
            gnu_os = parts[1]
        elif len(parts) == 1:
            if parts[0] in _GNUTriplet.UNKNOWN_OS_ALIASES:
                gnu_vendor = None
                gnu_os = parts[0]
            elif parts[0] in cls.OS_TO_GNU_OS_LUT.values():
                gnu_vendor = None
                gnu_os = parts[0]
            else:
                gnu_vendor = parts[0]
                gnu_os = None
        else:
            gnu_vendor = None
            gnu_os = None

        return cls(gnu_machine, gnu_vendor, gnu_os, gnu_abi)


    ARCH_TO_GNU_MACHINE_LUT = {
        "x86": "i686",
        "x86_64": "x86_64",
        "armv7": "arm",
        "armv7hf": "arm",
        "armv8": "aarch64",
        "riscv32": "riscv32",
        "riscv64": "riscv64",
    }

    @classmethod
    def calculate_gnu_machine(cls, archos: _ArchOs) -> str:
        return cls.ARCH_TO_GNU_MACHINE_LUT[archos.arch]

    UNKNOWN_OS_ALIASES = (
        "unknown",
        "none",
    )

    OS_TO_GNU_OS_LUT = {
        "baremetal": "none",
        "Android": "linux",
        "FreeBSD": "freebsd",
        "Linux": "linux",
        "Macos": "darwin",
        "Windows": "mingw32",
    }

    @classmethod
    def calculate_gnu_os(cls, archos: _ArchOs) -> typing.Optional[str]:
        if archos.os in ("baremetal", ):
            if archos.arch in ("x86", "x86_64", ):
                return None
            elif archos.arch in ("riscv32", "riscv64"):
                return "unknown"
        return cls.OS_TO_GNU_OS_LUT[archos.os]

    OS_TO_GNU_VENDOR_LUT = {
        "Windows": "w64",
        "baremetal": None,
    }

    @classmethod
    def calculate_gnu_vendor(cls, archos: _ArchOs) -> typing.Optional[str]:
        if archos.os in ("baremetal", "Android"):
            return None
        if archos.os in ("Macos", "iOS", "tvOS", "watchOS"):
            return "apple"
        return cls.OS_TO_GNU_VENDOR_LUT.get(archos.os, "pc")

    @classmethod
    def calculate_gnu_abi(self, archos: _ArchOs) -> typing.Optional[str]:
        if archos.os in ("baremetal", ):
            if archos.arch in ("armv7",):
                return "eabi"
            else:
                return "elf"
        abi_start = None
        if archos.os in ("Linux", ):
            abi_start = "gnu"
        elif archos.os in ("Android", ):
            abi_start = "android"
        else:
            return None
        if archos.arch in ("armv7",):
            abi_suffix = "eabi"
        elif archos.arch in ("armv7hf",):
            abi_suffix = "eabihf"
        else:
            abi_suffix = ""
        if archos.os in ("Android", ):
            abi_suffix += str(archos.extra.get("os.api_level", ""))

        return abi_start + abi_suffix

    KNOWN_GNU_ABIS = (
        "android",
        "gnu",
        "eabi",
        "elf",
    )

    def __eq__(self, other: object) -> bool:
        if type(self) != type(other):
            return False
        other: "_GNUTriplet"
        return self.machine == other.machine and self.vendor == other.vendor and self.os == other.os and self.abi == other.abi

    def __repr__(self) -> str:
        def x(v):
            if v is None:
                return None
            return f"'{v}'"
        return f"<{type(self).__name__}:machine={x(self.machine)},vendor={x(self.vendor)},os={x(self.os)},abi={x(self.abi)}>"


class _TestOsArch2GNUTriplet(unittest.TestCase):
    def test_linux_x86(self):
        archos = _ArchOs(arch="x86", os="Linux")
        self._test_osarch_to_gnutriplet(archos, _GNUTriplet(machine="i686", vendor="pc", os="linux", abi="gnu"), "i686-pc-linux-gnu")
        self.assertEqual(_ArchOs("x86", "Linux"), _ArchOs.from_triplet(_GNUTriplet.from_text("i386-linux")))
        self.assertEqual(_ArchOs("x86", "Linux"), _ArchOs.from_triplet(_GNUTriplet.from_text("i686-linux")))
        self.assertEqual(_GNUTriplet("i486", None, "linux", None), _GNUTriplet.from_text("i486-linux"))
        self.assertTrue(archos.is_compatible(_GNUTriplet.from_text("i486-linux")))
        self.assertTrue(archos.is_compatible(_GNUTriplet.from_text("i486-linux-gnu")))

    def test_linux_x86_64(self):
        self._test_osarch_to_gnutriplet(_ArchOs(arch="x86_64", os="Linux"), _GNUTriplet(machine="x86_64", vendor="pc", os="linux", abi="gnu"), "x86_64-pc-linux-gnu")

    def test_linux_armv7(self):
        archos = _ArchOs(arch="armv7", os="Linux")
        self._test_osarch_to_gnutriplet(archos, _GNUTriplet(machine="arm", vendor="pc", os="linux", abi="gnueabi"), "arm-pc-linux-gnueabi")
        self.assertEqual(_GNUTriplet("arm", "pc", None, "gnueabi"), _GNUTriplet.from_text("arm-pc-gnueabi"))
        self.assertEqual(_GNUTriplet("arm", "pc", None, "eabi"), _GNUTriplet.from_text("arm-pc-eabi"))
        self.assertEqual(_ArchOs("armv7hf", "baremetal"), _ArchOs.from_triplet(_GNUTriplet.from_text("arm-pc-gnueabihf")))
        self.assertTrue(archos.is_compatible(_GNUTriplet.from_text("arm-linux-gnueabi")))
        self.assertTrue(archos.is_compatible(_GNUTriplet.from_text("arm-linux-eabi")))
        self.assertFalse(archos.is_compatible(_GNUTriplet.from_text("arm-pc-linux-gnueabihf")))
        self.assertFalse(archos.is_compatible(_GNUTriplet.from_text("arm-pc-gnueabihf")))

    def test_linux_armv7hf(self):
        archos = _ArchOs(arch="armv7hf", os="Linux")
        self._test_osarch_to_gnutriplet(archos, _GNUTriplet(machine="arm", vendor="pc", os="linux", abi="gnueabihf"), "arm-pc-linux-gnueabihf")
        self.assertEqual(_GNUTriplet("arm", "pc", None, "gnueabihf"), _GNUTriplet.from_text("arm-pc-gnueabihf"))
        self.assertEqual(_ArchOs("armv7", "baremetal"), _ArchOs.from_triplet(_GNUTriplet.from_text("arm-pc-gnueabi")))
        self.assertFalse(archos.is_compatible(_GNUTriplet.from_text("arm-linux-gnueabi")))
        self.assertFalse(archos.is_compatible(_GNUTriplet.from_text("arm-linux-eabi")))
        self.assertTrue(archos.is_compatible(_GNUTriplet.from_text("arm-pc-linux-gnueabihf")))
        self.assertFalse(archos.is_compatible(_GNUTriplet.from_text("arm-pc-gnueabihf")))

    def test_windows_x86(self):
        self._test_osarch_to_gnutriplet(_ArchOs(arch="x86", os="Windows"), _GNUTriplet(machine="i686", vendor="w64", os="mingw32", abi=None), "i686-w64-mingw32")

    def test_windows_x86_64(self):
        self._test_osarch_to_gnutriplet(_ArchOs(arch="x86_64", os="Windows"), _GNUTriplet(machine="x86_64", vendor="w64", os="mingw32", abi=None), "x86_64-w64-mingw32")

    def test_macos_x86_64(self):
        self._test_osarch_to_gnutriplet(_ArchOs(arch="x86_64", os="Macos"), _GNUTriplet(machine="x86_64", vendor="apple", os="darwin", abi=None), "x86_64-apple-darwin")

    def test_freebsd_x86_64(self):
        self._test_osarch_to_gnutriplet(_ArchOs(arch="x86_64", os="FreeBSD"), _GNUTriplet(machine="x86_64", vendor="pc", os="freebsd", abi=None), "x86_64-pc-freebsd")

    def test_baremetal_x86(self):
        self._test_osarch_to_gnutriplet(_ArchOs(arch="x86", os="baremetal"), _GNUTriplet(machine="i686", vendor=None, os=None, abi="elf"), "i686-elf")

    def test_baremetal_x86_64(self):
        archos = _ArchOs(arch="x86_64", os="baremetal")
        self._test_osarch_to_gnutriplet(archos, _GNUTriplet(machine="x86_64", vendor=None, os=None, abi="elf"), "x86_64-elf")
        self.assertTrue(archos.is_compatible(_GNUTriplet.from_text("x86_64-elf")))
        self.assertTrue(archos.is_compatible(_GNUTriplet.from_text("x86_64-none-elf")))
        self.assertTrue(archos.is_compatible(_GNUTriplet.from_text("x86_64-unknown-elf")))

    def test_baremetal_armv7(self):
        archos = _ArchOs(arch="armv7", os="baremetal")
        self._test_osarch_to_gnutriplet(archos, _GNUTriplet(machine="arm", vendor=None, os="none", abi="eabi"), "arm-none-eabi")
        self.assertTrue(archos.is_compatible(_GNUTriplet.from_text("arm-none-eabi")))

    def test_baremetal_armv8(self):
        self._test_osarch_to_gnutriplet(_ArchOs(arch="armv8", os="baremetal"), _GNUTriplet(machine="aarch64", vendor=None, os="none", abi="elf"), "aarch64-none-elf")

    def test_baremetal_riscv32(self):
        self._test_osarch_to_gnutriplet(_ArchOs(arch="riscv32", os="baremetal"), _GNUTriplet(machine="riscv32", vendor=None, os="unknown", abi="elf"), "riscv32-unknown-elf")

    def test_baremetal_riscv64(self):
        self._test_osarch_to_gnutriplet(_ArchOs(arch="riscv64", os="baremetal"), _GNUTriplet(machine="riscv64", vendor=None, os="unknown", abi="elf"), "riscv64-unknown-elf")

    def test_android_armv7(self):
        self._test_osarch_to_gnutriplet(_ArchOs(arch="armv7", os="Android", extra={"os.api_level": "31"}), _GNUTriplet(machine="arm", vendor=None, os="linux", abi="androideabi31"), "arm-linux-androideabi31")

    def test_android_armv8(self):
        self._test_osarch_to_gnutriplet(_ArchOs(arch="armv8", os="Android", extra={"os.api_level": "24"}), _GNUTriplet(machine="aarch64", vendor=None, os="linux", abi="android24"), "aarch64-linux-android24")

    def test_android_x86(self):
        self._test_osarch_to_gnutriplet(_ArchOs(arch="x86", os="Android", extra={"os.api_level": "16"}), _GNUTriplet(machine="i686", vendor=None, os="linux", abi="android16"), "i686-linux-android16")

    def test_android_x86_64(self):
        self._test_osarch_to_gnutriplet(_ArchOs(arch="x86_64", os="Android", extra={"os.api_level": "29"}), _GNUTriplet(machine="x86_64", vendor=None, os="linux", abi="android29"), "x86_64-linux-android29")
        self.assertEqual(_ArchOs(arch="x86_64", os="Android", extra={"os.api_level": "25"}), _ArchOs.from_triplet(_GNUTriplet.from_text("x86_64-linux-android29")))

    def _test_osarch_to_gnutriplet(self, archos: _ArchOs, gnuobj_ref: _GNUTriplet, triplet_ref: str):
        gnuobj = _GNUTriplet.from_archos(archos)
        self.assertEqual(gnuobj_ref, gnuobj)
        self.assertEqual(triplet_ref, gnuobj.triplet)
        self.assertEqual(gnuobj_ref, _GNUTriplet.from_text(triplet_ref))
        # self.assertEqual(triplet_ref, tools.get_gnu_triplet(archos.os, archos.arch, compiler="gcc"))
