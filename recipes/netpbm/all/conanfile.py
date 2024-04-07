import os
import shutil

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, save, replace_in_file, chdir, rmdir, rm, rename, copy
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout


class NetpbmConan(ConanFile):
    name = "netpbm"
    description = "Netpbm is a toolkit for manipulation of graphic images, including conversion of images between a variety of different formats."
    license = "IJG AND BSD-3-Clause AND GPL-2.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://netpbm.sourceforge.net"
    topics = ("image", "graphics", "image-processing", "image-conversion", "pbm")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tools": [True, False],
        "with_libjpeg": ["libjpeg", "libjpeg-turbo", "mozjpeg"],
        "with_x11": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "tools": False,
        "with_libjpeg": "libjpeg",
        "with_x11": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_x11

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("jasper/4.2.0")
        self.requires("libpng/[>=1.6 <2]")
        self.requires("libtiff/4.6.0")
        self.requires("libxml2/2.12.5")
        self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.2")
        elif self.options.with_libjpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.5")
        if self.options.get_safe("with_x11"):
            self.requires("xorg/system")
        # TODO: add ghostscript to CCI
        # TODO: add jbigkit to CCI

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.1.0")
        self.tool_requires("make/4.4.1")
        self.tool_requires("flex/2.6.4")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _libtype_and_suffix(self):
        if self.settings.os == "Windows":
            return "dll", "dll"
        elif is_apple_os(self):
            if self.options.shared:
                return "dylib", "dylib"
            else:
                return "unixstatic", "a"
        else:
            if self.options.shared:
                return "unixshared", "so"
            else:
                return "unixstatic", "a"

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        config = []
        lib_type, suffix = self._libtype_and_suffix
        config.append(f"NETPBMLIBTYPE={lib_type}")
        config.append(f"NETPBMLIBSUFFIX={suffix}")
        config.append(f"STATICLIB_TOO={'N' if self.options.shared else 'Y'}")
        config.append(f"WANT_SSE={'Y' if self.settings.arch in ['x86', 'x86_64'] else 'N'}")
        config.append("DEFAULT_TARGET=nonmerge")
        config.append("LDRELOC=ld --reloc")

        if is_apple_os(self):
            config.append("LDSHLIB=-shared -dynamiclib -install_name @rpath/libnetpbm.dylib")

        def _configure_dependency(name, pkg, lib):
            cpp_info = self.dependencies[pkg].cpp_info.aggregated_components()
            # The file does not need to exist. The build script simply strips 'lib*.a' from the paths.
            lib_path = os.path.join(cpp_info.libdir, f"lib{lib}.a")
            config.append(f"{name}LIB={lib_path}")
            config.append(f"{name}HDR_DIR={cpp_info.includedir}")

        def _use_pkgconfig(name):
            config.append(f"{name}LIB=USE_PKGCONFIG.a")
            config.append(f"{name}HDR_DIR=USE_PKGCONFIG.a")

        _configure_dependency("TIFF", "libtiff", "tiff")
        _configure_dependency("PNG", "libpng", "png")
        _configure_dependency("JPEG", str(self.options.with_libjpeg), "jpeg")
        _configure_dependency("JASPER", "jasper", "jasper")
        # _configure_dependency("JBIG", "jbigkit", "jbig")
        if self.options.get_safe("with_x11"):
            _use_pkgconfig("X11")

        cflags = list(tc.cflags)
        if self.settings.build_type == "Debug":
            cflags += ["-g"]
        else:
            # Match flags set by ./configure
            cflags += ["-O3", "-ffast-math", "-fno-finite-math-only"]
        if self.options.get_safe("fPIC", True):
            cflags.append("-fPIC")
        if is_apple_os(self):
            # For vasprintf
            cflags.append("-D_DARWIN_C_SOURCE")
        config.append(f"CFLAGS={' '.join(cflags)}")

        tc.make_args.extend(config)
        tc.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def _patch_sources(self):
        # Fix FILE not being defined in jpeglib.h
        replace_in_file(self, os.path.join(self.source_folder, "converter", "other", "cameratopam", "camera.c"),
                        "#include <jpeglib.h>", "#include <stdio.h>\n#include <jpeglib.h>")
        # add missing -ljpeg to cameratopam
        save(self, os.path.join(self.source_folder, "converter", "other", "cameratopam", "Makefile"),
             "\ncameratopam: LDFLAGS_TARGET = $(shell $(LIBOPT) $(LIBOPTR) $(JPEGLIB))\n", append=True)

        if not self.options.tools:
            replace_in_file(self, os.path.join(self.source_folder, "GNUmakefile"),
                            "PROG_SUBDIRS =", "PROG_SUBDIRS = #")

    def build(self):
        self._patch_sources()
        with chdir(self, self.source_folder):
            shutil.copy("config.mk.in", "config.mk")
            autotools = Autotools(self)
            autotools.make()

    def package(self):
        for file in ["copyright_summary", "patent_summary", "GPL_LICENSE.txt", "lgpl_v21.txt", "COPYRIGHT.PATENT"]:
            copy(self, file, os.path.join(self.source_folder, "doc"), os.path.join(self.package_folder, "licenses"))
        temp_dir = self.package_path.joinpath("tmp")
        lib_dir = temp_dir.joinpath("lib")
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make(target="package", args=[f"pkgdir={temp_dir}"])
        if self.options.shared:
            if is_apple_os(self):
                soname_file = next(lib_dir.glob("libnetpbm.*.*.dylib"))
                rename(self, soname_file, lib_dir.joinpath("libnetpbm.dylib"))
                rm(self, "libnetpbm.*.dylib", lib_dir)
            else:
                soname_file = next(lib_dir.glob("libnetpbm.so.*")).name
                self.run(f"ln -s {soname_file} libnetpbm.so", cwd=lib_dir)
        else:
            copy(self, "*.a", os.path.join(self.source_folder, "lib"), lib_dir)
        rename(self, os.path.join(temp_dir, "include"), os.path.join(self.package_folder, "include"))
        rename(self, os.path.join(temp_dir, "lib"), os.path.join(self.package_folder, "lib"))
        rename(self, os.path.join(temp_dir, "misc"), os.path.join(self.package_folder, "res"))
        if self.options.tools:
            rename(self, os.path.join(temp_dir, "bin"), os.path.join(self.package_folder, "bin"))
        rmdir(self, temp_dir)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "netpbm")
        self.cpp_info.libs = ["netpbm"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        self.cpp_info.requires.extend([
            "jasper::jasper",
            "libpng::libpng",
            "libtiff::libtiff",
            "libxml2::libxml2",
            "zlib::zlib",
        ])
        if self.options.with_libjpeg == "libjpeg":
            self.cpp_info.requires.append("libjpeg::libjpeg")
        elif self.options.with_libjpeg == "libjpeg-turbo":
            self.cpp_info.requires.append("libjpeg-turbo::jpeg")
        elif self.options.with_libjpeg == "mozjpeg":
            self.cpp_info.requires.append("mozjpeg::libjpeg")
        if self.options.get_safe("with_x11"):
            self.cpp_info.requires.append("xorg::x11")
