import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import export_conandata_patches, apply_conandata_patches, copy, get, rm, rmdir, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc

required_conan_version = ">=2.15"


class ElfutilsConan(ConanFile):
    name = "elfutils"
    description = "A dwarf, dwfl and dwelf functions to read DWARF, find separate debuginfo, symbols and inspect process state."
    homepage = "https://sourceware.org/elfutils"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("libelf", "libdw", "libasm")
    license = ["GPL-1.0-or-later", "LGPL-3.0-or-later", "GPL-2.0-or-later"]

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "debuginfod": [True, False],
        "libdebuginfod": [True, False],
        "with_bzlib": [True, False],
        "with_lzma": [True, False],
        "with_zstd": [True, False],
        "with_sqlite3": [True, False],
        "sanitize_memory": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "debuginfod": False,
        "libdebuginfod": False,
        "with_bzlib": True,
        "with_lzma": True,
        "with_zstd": True,
        "with_sqlite3": False,
        "sanitize_memory": False,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_sqlite3:
            self.requires("sqlite3/3.44.2")
        if self.options.with_bzlib:
            self.requires("bzip2/1.0.8")
        if self.options.with_lzma:
            self.requires("xz_utils/[>=5.4.5 <6]")
        if self.options.get_safe("with_zstd"):
            self.requires("zstd/[~1.5]")
        if self.options.get_safe("libdebuginfod"):
            self.requires("libcurl/[>=7.78.0 <9]")
        if self.options.debuginfod:
            self.requires("libmicrohttpd/0.9.75")

    def build_requirements(self):
        self.tool_requires("gettext/0.22.5")
        self.tool_requires("automake/1.16.5")
        self.build_requires("m4/1.4.19")
        self.build_requires("flex/2.6.4")
        self.tool_requires("bison/3.8.2")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def validate(self):
        # Note that elfutils cannot be built on macOS
        # Example Error: "configure: error: __thread support required"
        # Reference: https://stackoverflow.com/questions/72372589/elfutils-build-error-on-mac-configure-error-thread-support-required
        if self.settings.os == "Macos":
            raise ConanInvalidConfiguration("elfutils does not support macOS.")

        if is_msvc(self):
            raise ConanInvalidConfiguration(f"Your compiler {self.settings.compiler} is not supported. "
                                            "elfutils only supports GCC and Clang.")

        if self.settings.compiler != "gcc":
            self.output.warning(f"Your compiler {self.settings.compiler} is not GCC.")

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
            "--with-zstd" if self.options.get_safe("with_zstd") else "--without-zstd",
            "--enable-debuginfod" if self.options.debuginfod else "--disable-debuginfod",
        ])
        tc.configure_args.append("--enable-libdebuginfod" if self.options.libdebuginfod else "--disable-libdebuginfod")
        if self.options.sanitize_memory:
            tc.configure_args.append("--enable-sanitize-memory")
        tc.configure_args.append(f"BUILD_STATIC={'0' if self.options.shared else '1'}")
        if self.options.get_safe("with_zstd"):
            # ./configure ignores system_libs
            tc.extra_ldflags.append("-pthread")

        if self.settings.os == "Linux":
            libdirs_host = [l for dependency in self.dependencies.host.values() for l in dependency.cpp_info.aggregated_components().libdirs]
            tc.extra_ldflags.extend([f"-Wl,-rpath-link,{libdir}" for libdir in libdirs_host])
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "config", "eu.am"),
                        "-Werror", "", strict=False)

    def build(self):
        self._patch_sources()
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
        self.cpp_info.components["libelf"].set_property("pkg_config_name", "libelf")
        if self.options.with_bzlib:
            self.cpp_info.components["libelf"].requires.append("bzip2::bzip2")
        if self.options.with_lzma:
            self.cpp_info.components["libelf"].requires.append("xz_utils::xz_utils")
        if self.options.get_safe("with_zstd"):
            self.cpp_info.components["libelf"].requires.append("zstd::zstd")
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["libelf"].system_libs.append("pthread")

        self.cpp_info.components["libdw"].libs = ["dw"]
        self.cpp_info.components["libdw"].requires = ["libelf"]
        self.cpp_info.components["libdw"].set_property("pkg_config_name", "libdw")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libdw"].system_libs.extend(["dl"])

        self.cpp_info.components["libasm"].includedirs = ["include/elfutils"]
        self.cpp_info.components["libasm"].libs = ["asm"]
        self.cpp_info.components["libasm"].requires = ["libelf", "libdw"]

        if self.options.get_safe("libdebuginfod"):
            self.cpp_info.components["libdebuginfod"].libs = ["debuginfod"]
            self.cpp_info.components["libdebuginfod"].requires = ["libcurl::curl"]
            self.cpp_info.components["libdebuginfod"].set_property("pkg_config_name", "libdebuginfod")

        # utilities
        bin_path = os.path.join(self.package_folder, "bin")
        lib_path = os.path.join(self.package_folder, "lib")
        self.buildenv_info.prepend_path("PATH", bin_path)
        self.buildenv_info.prepend_path("LD_LIBRARY_PATH", lib_path)
