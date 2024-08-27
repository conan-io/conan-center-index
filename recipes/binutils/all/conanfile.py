import os
import re
import typing
import unittest

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path

required_conan_version = ">=1.54.0"

# This recipe includes a selftest to test conversion of os/arch to triplets (and vice verse)
# Run it using `python -m unittest conanfile.py`


class BinutilsConan(ConanFile):
    name = "binutils"
    description = "The GNU Binutils are a collection of binary tools."
    package_type = "application"
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index/"
    homepage = "https://www.gnu.org/software/binutils"
    topics = ("gnu", "ld", "linker", "as", "assembler", "objcopy", "objdump")
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "multilib": [True, False],
        "with_libquadmath": [True, False],
        "target_arch": [None, "ANY"],
        "target_os": [None, "ANY"],
        "target_triplet": [None, "ANY"],
        "prefix": [None, "ANY"],
    }

    default_options = {
        "multilib": True,
        "with_libquadmath": True,
        "target_arch": None,  # Initialized in configure, checked in validate
        "target_os": None,  # Initialized in configure, checked in validate
        "target_triplet": None,  # Initialized in configure, checked in validate
        "prefix": None,  # Initialized in configure (NOT config_options, because it depends on target_{arch,os})
    }

    def layout(self):
        basic_layout(self, src_folder="src")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _settings_target(self):
        return getattr(self, "settings_target", None) or self.settings

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

        if not self.options.target_triplet:
            if not self.options.target_arch:
                # If target triplet and target arch are not set, initialize it from the target settings
                self.options.target_arch = str(self._settings_target.arch)
            if not self.options.target_os:
                # If target triplet and target os are not set, initialize it from the target settings
                self.options.target_os = str(self._settings_target.os)
            # Initialize the target_triplet from the target arch and target os
            self.options.target_triplet = _GNUTriplet.from_archos(_ArchOs(
                arch=str(self.options.target_arch),
                os=str(self.options.target_os),
                extra=dict(self._settings_target.values_list))).triplet
        else:
            gnu_triplet_obj = _GNUTriplet.from_text(str(self.options.target_triplet))
            archos = _ArchOs.from_triplet(gnu_triplet_obj)
            if not self.options.target_arch:
                # If target arch is not set, deduce it from the target triplet
                self.options.target_arch = archos.arch
            if not self.options.target_os:
                # If target arch is not set, deduce it from the target triplet
                self.options.target_os = archos.os

        if not self.options.prefix:
            self.options.prefix = f"{self.options.target_triplet}-"

        self.output.info(f"binutils:target_arch={self.options.target_arch}")
        self.output.info(f"binutils:target_os={self.options.target_os}")
        self.output.info(f"binutils:target_triplet={self.options.target_triplet}")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("This recipe does not support building binutils by this compiler")

        if self.options.target_os == "Macos":
            raise ConanInvalidConfiguration("cci does not support building binutils for Macos since binutils is degraded there (no as/ld + armv8 does not build)")

        # Check whether the actual target_arch and target_os option are valid (they should be in settings.yml)
        # FIXME: does there exist a stable Conan API to accomplish this?
        if str(self.options.target_arch) not in self.settings.arch.values_range:
            raise ConanInvalidConfiguration(f"target_arch={self.options.target_arch} is invalid (possibilities={self.settings.arch.values_range})")
        if str(self.options.target_os) not in self.settings.os.values_range:
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
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type="str"):
                self.tool_requires("msys2/cci.latest")
        self.tool_requires("bison/3.8.2")
        self.tool_requires("flex/2.6.4")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _exec_prefix(self):
        return os.path.join("bin", "exec_prefix")

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        def yes_no(opt): return "yes" if opt else "no"
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--disable-nls")
        tc.configure_args.append(f"--target={self.options.target_triplet}")
        tc.configure_args.append(f"--enable-multilib={yes_no(self.options.multilib)}")
        tc.configure_args.append(f"--with-zlib={unix_path(self, self.dependencies['zlib'].package_folder)}")
        tc.configure_args.append(f"--program-prefix={self.options.prefix}")
        tc.configure_args.append("--exec_prefix=/bin/exec_prefix")
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()

        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"), recursive=True)
        copy(
            self,
            pattern="COPYING*",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
            keep_path=False,
        )

    def package_info(self):
        target_bindir = os.path.join(self._exec_prefix, str(self.options.target_triplet), "bin")
        self.cpp_info.bindirs = ["bin", target_bindir]

        absolute_target_bindir = os.path.join(self.package_folder, target_bindir)

        # v1 exports
        bindir = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bindir)
        self.env_info.PATH.append(absolute_target_bindir)
        self.output.info(f"GNU triplet={self.options.target_triplet}")
        self.user_info.gnu_triplet = self.options.target_triplet
        self.user_info.prefix = self.options.prefix
        self.output.info(f"executable prefix={self.options.prefix}")

        # v2 exports
        self.buildenv_info.append_path("PATH", bindir)
        self.buildenv_info.append_path("PATH", absolute_target_bindir)

        # Add recipe path to enable running the self test in the test package.
        # Don't use this property in production code. It's unsupported.
        self.user_info.recipe_path = os.path.realpath(__file__)
        self.cpp_info.resdirs = ["etc"]
        self.buildenv_info.define("GPROFNG_SYSCONFDIR", os.path.join(self.package_folder, "etc"))
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["dl", "rt"]

class _ArchOs:
    def __init__(self, arch: str, os: str, extra: typing.Optional[typing.Dict[str, str]] = None):
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
        _os = cls.calculate_os(triplet)
        extra = {}

        if _os == "Android" and triplet.abi:
            m = re.match(".*([0-9]+)", triplet.abi)
            if m:
                extra["os.api_level"] = m.group(1)

        # Assume first architecture
        return cls(arch=archs[0], os=_os, extra=extra)

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
        if any(v in parts[-1] for v in cls.KNOWN_GNU_ABIS):
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
