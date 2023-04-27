from conan import ConanFile, Version
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.files import export_conandata_patches, apply_conandata_patches, copy, get, rm, rmdir
from conan.tools.microsoft import unix_path
import os

required_conan_version = ">=1.54.0"


class ElfutilsConan(ConanFile):
    name = "elfutils"
    description = "A dwarf, dwfl and dwelf functions to read DWARF, find separate debuginfo, symbols and inspect process state."
    homepage = "https://sourceware.org/elfutils"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("elfutils", "libelf", "libdw", "libasm")
    license = ["GPL-1.0-or-later", "LGPL-3.0-or-later", "GPL-2.0-or-later"]

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "debuginfod": [True, False],
        "libdebuginfod": [True, False],
        "with_bzlib": [True, False],
        "with_lzma": [True, False],
        "with_sqlite3": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "debuginfod": False,
        "libdebuginfod": False,
        "with_bzlib": True,
        "with_lzma": True,
        "with_sqlite3": False,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
        if Version(self.version) < "0.186":
            del self.options.libdebuginfod

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/1.2.12") # TODO: 1.2.13
        if self.options.with_sqlite3:
            self.requires("sqlite3/3.38.5") # TODO: sqlite3/3.41.1
        if self.options.with_bzlib:
            self.requires("bzip2/1.0.8")
        if self.options.with_lzma:
            self.requires("xz_utils/5.2.5") # TODO: xz_utils
        if self.options.get_safe("libdebuginfod"):
            self.requires("libcurl/7.83.0") # TODO: libcurl/8.0.1
        if self.options.debuginfod:
            self.requires("libmicrohttpd/0.9.75")

    def build_requirements(self):
        self.build_requires("gettext/0.21")
        self.build_requires("automake/1.16.5")
        self.build_requires("m4/1.4.19")
        self.build_requires("flex/2.6.4")
        self.build_requires("bison/3.8.2")
        self.build_requires("pkgconf/1.9.3")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def validate(self):
        if Version(self.version) >= "0.186":
            if self.settings.compiler in ["apple-clang", "msvc"]:
                raise ConanInvalidConfiguration(f"Your compiler {self.settings.compiler} is not supported. "
                                                "elfutils only supports GCC and Clang.")
        else:
            if self.settings.compiler in ["clang", "apple-clang", "msvc"]:
                raise ConanInvalidConfiguration(f"Your compiler {self.settings.compiler} is not supported. "
                                                "elfutils only supports GCC.")
        if self.settings.compiler != "gcc":
            self.output.warn(f"Your compiler {self.settings.compiler} is not GCC.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--disable-werror",
            "--enable-static={}".format("no" if self.options.shared else "yes"),
            "--enable-deterministic-archives",
            "--enable-silent-rules",
            "--with-zlib",
            "--with-bzlib" if self.options.with_bzlib else "--without-bzlib",
            "--with-lzma" if self.options.with_lzma else "--without-lzma",
            "--enable-debuginfod" if self.options.debuginfod else "--disable-debuginfod",
        ])
        if Version(self.version) >= "0.186":
            tc.configure_args.append("--enable-libdebuginfod" if self.options.libdebuginfod else "--disable-libdebuginfod")
        tc.configure_args.append(f"BUILD_STATIC={'0' if self.options.shared else '1'}")
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.autoreconf(args=["-fiv"])
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, pattern="COPYING*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "etc"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.options.shared:
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))
        else:
            rm(self, "*.so", os.path.join(self.package_folder, "lib"))
            rm(self, "*.so.1", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        # library components
        self.cpp_info.components["libelf"].libs = ["elf"]
        self.cpp_info.components["libelf"].requires = ["zlib::zlib"]

        self.cpp_info.components["libdw"].libs = ["dw"]
        self.cpp_info.components["libdw"].requires = ["libelf", "zlib::zlib"]
        if self.options.with_bzlib:
            self.cpp_info.components["libdw"].requires.append("bzip2::bzip2")
        if self.options.with_lzma:
            self.cpp_info.components["libdw"].requires.append("xz_utils::xz_utils")

        self.cpp_info.components["libasm"].includedirs = ["include/elfutils"]
        self.cpp_info.components["libasm"].libs = ["asm"]
        self.cpp_info.components["libasm"].requires = ["libelf", "libdw"]

        if self.options.get_safe("libdebuginfod"):
            self.cpp_info.components["libdebuginfod"].libs = ["debuginfod"]
            self.cpp_info.components["libdebuginfod"].requires = ["libcurl::curl"]

        # utilities
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        bin_ext = ".exe" if self.settings.os == "Windows" else ""

        addr2line = unix_path(self, os.path.join(self.package_folder, "bin", "eu-addr2line" + bin_ext))
        self.output.info("Setting ADDR2LINE to {}".format(addr2line))
        self.env_info.ADDR2LINE = addr2line

        ar = unix_path(self, os.path.join(self.package_folder, "bin", "eu-ar" + bin_ext))
        self.output.info("Setting AR to {}".format(ar))
        self.env_info.AR = ar

        elfclassify = unix_path(self, os.path.join(self.package_folder, "bin", "eu-elfclassify" + bin_ext))
        self.output.info("Setting ELFCLASSIFY to {}".format(elfclassify))
        self.env_info.ELFCLASSIFY = elfclassify

        elfcmp = unix_path(self, os.path.join(self.package_folder, "bin", "eu-elfcmp" + bin_ext))
        self.output.info("Setting ELFCMP to {}".format(elfcmp))
        self.env_info.ELFCMP = elfcmp

        elfcompress = unix_path(self, os.path.join(self.package_folder, "bin", "eu-elfcompress" + bin_ext))
        self.output.info("Setting ELFCOMPRESS to {}".format(elfcompress))
        self.env_info.ELFCOMPRESS = elfcompress

        elflint = unix_path(self, os.path.join(self.package_folder, "bin", "eu-elflint" + bin_ext))
        self.output.info("Setting ELFLINT to {}".format(elflint))
        self.env_info.ELFLINT = elflint

        findtextrel = unix_path(self, os.path.join(self.package_folder, "bin", "eu-findtextrel" + bin_ext))
        self.output.info("Setting FINDTEXTREL to {}".format(findtextrel))
        self.env_info.FINDTEXTREL = findtextrel

        make_debug_archive = unix_path(self, os.path.join(self.package_folder, "bin", "eu-make-debug-archive" + bin_ext))
        self.output.info("Setting MAKE_DEBUG_ARCHIVE to {}".format(make_debug_archive))
        self.env_info.MAKE_DEBUG_ARCHIVE = make_debug_archive

        nm = unix_path(self, os.path.join(self.package_folder, "bin", "eu-nm" + bin_ext))
        self.output.info("Setting NM to {}".format(nm))
        self.env_info.NM = nm

        objdump = unix_path(self, os.path.join(self.package_folder, "bin", "eu-objdump" + bin_ext))
        self.output.info("Setting OBJDUMP to {}".format(objdump))
        self.env_info.OBJDUMP = objdump

        ranlib = unix_path(self, os.path.join(self.package_folder, "bin", "eu-ranlib" + bin_ext))
        self.output.info("Setting RANLIB to {}".format(ranlib))
        self.env_info.RANLIB = ranlib

        readelf = unix_path(self, os.path.join(self.package_folder, "bin", "eu-readelf" + bin_ext))
        self.output.info("Setting READELF to {}".format(readelf))
        self.env_info.READELF = readelf

        size = unix_path(self, os.path.join(self.package_folder, "bin", "eu-size" + bin_ext))
        self.output.info("Setting SIZE to {}".format(size))
        self.env_info.SIZE = size

        stack = unix_path(self, os.path.join(self.package_folder, "bin", "eu-stack" + bin_ext))
        self.output.info("Setting STACK to {}".format(stack))
        self.env_info.STACK = stack

        strings = unix_path(self, os.path.join(self.package_folder, "bin", "eu-strings" + bin_ext))
        self.output.info("Setting STRINGS to {}".format(strings))
        self.env_info.STRINGS = strings

        strip = unix_path(self, os.path.join(self.package_folder, "bin", "eu-strip" + bin_ext))
        self.output.info("Setting STRIP to {}".format(strip))
        self.env_info.STRIP = strip

        unstrip = unix_path(self, os.path.join(self.package_folder, "bin", "eu-unstrip" + bin_ext))
        self.output.info("Setting UNSTRIP to {}".format(unstrip))
        self.env_info.UNSTRIP = unstrip
