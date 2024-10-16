import glob
import os
import re
from pathlib import Path

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, to_apple_arch
from conan.tools.build import cross_building, can_run
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, collect_libs, copy, get, rm, rmdir, export_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, msvc_runtime_flag, unix_path
from conan.tools.scm import Version

required_conan_version = ">=1.53"


class RubyConan(ConanFile):
    name = "ruby"
    description = "The Ruby Programming Language"
    license = "Ruby"
    topics = ("ruby", "language", "object-oriented", "ruby-language")
    homepage = "https://www.ruby-lang.org"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_static_linked_ext": [True, False],
        "with_enable_load_relative": [True, False],
        "with_openssl": [True, False],
        "with_libyaml": [True, False],
        "with_libffi": [True, False],
        "with_readline": [True, False],
        "with_gmp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_static_linked_ext": True,
        "with_enable_load_relative": True,
        "with_openssl": True,
        "with_libyaml": True,
        "with_libffi": True,
        "with_readline": True,
        "with_gmp": True,
    }

    short_paths = True

    @property
    def _windows_system_libs(self):
        return ["user32", "advapi32", "shell32", "ws2_32", "iphlpapi", "imagehlp", "shlwapi", "bcrypt"]

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
            del self.options.with_static_linked_ext
        if self.settings.os == "Windows":
            # readline isn't supported on Windows
            del self.options.with_readline
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")
        if self.options.with_libyaml:
            self.requires("libyaml/0.2.5")
        if self.options.with_libffi:
            self.requires("libffi/3.4.6")
        if self.options.get_safe("with_readline"):
            self.requires("readline/8.2")
        if self.options.with_gmp:
            self.requires("gmp/6.3.0")

    def validate(self):
        if is_msvc(self) and is_msvc_static_runtime(self):
            # see https://github.com/conan-io/conan-center-index/pull/8644#issuecomment-1068974098
            raise ConanInvalidConfiguration("VS static runtime is not supported")

    def build_requirements(self):
        # Makefile calls autoconf
        self.tool_requires("autoconf/2.72")
        if not can_run(self):
            self.tool_requires(f"ruby/{self.version}")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        VirtualBuildEnv(self).generate()

        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--disable-install-doc")
        if not self.options.shared and self.options.with_static_linked_ext:
            tc.configure_args.append("--with-static-linked-ext")
        if self.options.with_enable_load_relative:
            tc.configure_args.append("--enable-load-relative")
        # Ruby doesn't respect the --with-gmp-dir for eg. After removal of libgmp-dev on conanio/gcc10 build failed
        opt_dirs = []
        # zlib always enabled
        tc.configure_args.append(f"--with-zlib-dir={unix_path(self, self.dependencies['zlib'].package_folder)}")
        for dep in ["zlib", "openssl", "libffi", "libyaml", "readline", "gmp"]:
            if self.options.get_safe(f"with_{dep}"):
                root_path = unix_path(self, self.dependencies[dep].package_folder)
                tc.configure_args.append(f"--with-{dep}-dir={root_path}")
                opt_dirs.append(root_path)
        if opt_dirs:
            tc.configure_args.append(f"--with-opt-dir={os.pathsep.join(opt_dirs)}")
        if is_apple_os(self) and cross_building(self):
            apple_arch = to_apple_arch(self.settings.arch)
            if apple_arch:
                tc.configure_args.append(f"--with-arch={apple_arch}")
        if is_msvc(self):
            tc.build_type_flags.append(f"-{msvc_runtime_flag(self)}")
            tc.build_type_flags = [f if f != "-O2" else "-O2sy-" for f in tc.build_type_flags]
        tc.generate()

        td = AutotoolsDeps(self)
        # remove non-existing frameworks dirs, otherwise clang complains
        for m in re.finditer(r"-F (\S+)", td.vars().get("LDFLAGS")):
            if not os.path.exists(m[1]):
                td.environment.remove("LDFLAGS", f"-F {m[1]}")
        if self.settings.os == "Windows":
            if is_msvc(self):
                td.environment.append("LIBS", [f"{lib}.lib" for lib in self._windows_system_libs])
            else:
                td.environment.append("LDFLAGS", [f"-l{lib}" for lib in self._windows_system_libs])
        td.generate()

    def build(self):
        autotools = Autotools(self)
        build_script_folder = self.source_folder
        if is_msvc(self):
            self.conf.define("tools.gnu:make_program", "nmake")
            build_script_folder = os.path.join(self.source_folder, "win32")
            if "TMP" in os.environ:  # workaround for TMP in CCI containing both forward and back slashes
                os.environ["TMP"] = os.environ["TMP"].replace("/", "\\")
        autotools.configure(build_script_folder=build_script_folder)
        autotools.make()

    def package(self):
        for file in ["COPYING", "BSDL"]:
            copy(self, pattern=file, src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

        # install the enc/*.a / ext/*.a libraries
        if not self.options.shared and self.options.with_static_linked_ext:
            for dirname in ["ext", "enc"]:
                dst = os.path.join("lib", dirname)
                copy(self, "*.a", src=dirname, dst=os.path.join(self.package_folder, dst), keep_path=True)
                copy(self, "*.lib", src=dirname, dst=os.path.join(self.package_folder, dst), keep_path=True)

    def package_info(self):
        version = Version(self.version)
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "Ruby")
        self.cpp_info.set_property("cmake_target_name", "Ruby::Ruby")
        self.cpp_info.set_property("pkg_config_name", "ruby")
        self.cpp_info.set_property("pkg_config_aliases", [f"ruby-{version.major}.{version.minor}"])

        config_file = glob.glob(os.path.join(self.package_folder, "include", "**", "ruby", "config.h"), recursive=True)[0]
        self.cpp_info.includedirs = [
            os.path.join(self.package_folder, "include", f"ruby-{version}"),
            str(Path(config_file).parent.parent),
        ]
        self.cpp_info.libs = collect_libs(self)
        if is_msvc(self):
            if self.options.shared:
                self.cpp_info.libs = [l for l in self.cpp_info.libs if not l.endswith("-static")]
            else:
                self.cpp_info.libs = [l for l in self.cpp_info.libs if l.endswith("-static")]

        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["dl", "pthread", "rt", "m", "util"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = self._windows_system_libs
        if str(self.settings.compiler) in ("clang", "apple-clang"):
            self.cpp_info.cflags = ["-fdeclspec"]
            self.cpp_info.cxxflags = ["-fdeclspec"]
        if is_apple_os(self):
            self.cpp_info.frameworks = ["CoreFoundation"]

        self.cpp_info.requires.append("zlib::zlib")
        if self.options.with_gmp:
            self.cpp_info.requires.append("gmp::gmp")
        if self.options.with_openssl:
            self.cpp_info.requires.append("openssl::openssl")
        if self.options.with_libyaml:
            self.cpp_info.requires.append("libyaml::libyaml")
        if self.options.with_libffi:
            self.cpp_info.requires.append("libffi::libffi")
        if self.options.get_safe("with_readline"):
            self.cpp_info.requires.append("readline::readline")
