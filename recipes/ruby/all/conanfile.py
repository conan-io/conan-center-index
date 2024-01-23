from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, to_apple_arch
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, PkgConfigDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import check_min_vs, is_msvc, is_msvc_static_runtime, msvc_runtime_flag, unix_path, VCVars
from conan.tools.scm import Version

import glob
import os

required_conan_version = ">=1.53"


class RubyConan(ConanFile):
    name = "ruby"
    description = "The Ruby Programming Language"
    license = "Ruby"
    topics = ("ruby", "c", "language", "object-oriented", "ruby-language")
    homepage = "https://www.ruby-lang.org"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],

        "with_static_linked_ext": [True, False],
        "with_enable_load_relative": [True, False],
        "with_libyaml": [True, False],
        "with_libffi": [True, False],
        "with_readline": [True, False],
        "with_gmp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": True,

        "with_static_linked_ext": True,
        "with_enable_load_relative": True,
        "with_libyaml": True,
        "with_libffi": True,
        "with_readline": True,
        "with_gmp": True,
    }

    short_paths = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _windows_system_libs(self):
        return ["user32", "advapi32", "shell32", "ws2_32", "iphlpapi", "imagehlp", "shlwapi", "bcrypt"]

    @property
    def _msvc_optflag(self):
        if check_min_vs(self, "190", raise_invalid=False):
            return "-O2sy-"
        else:  # MSVC < 14
            return "-O2b2xg-"

    def export_sources(self):
        export_conandata_patches(self)

    def build_requirements(self):
        if self.settings.os != "Windows":
            self.tool_requires("autoconf/2.71")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.1.0")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
            del self.options.with_static_linked_ext

        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

        if self.settings.os == "Windows":
            # readline isn't supported on Windows
            del self.options.with_readline

        if is_msvc(self):
            # conan libffi will not allow linking right now with MSVC
            del self.options.with_libffi
    def requirements(self):
        self.requires("zlib/1.2.12")

        if self.options.with_openssl:
            self.requires("openssl/1.1.1q")

        if self.options.with_libyaml:
            self.requires("libyaml/0.2.5")

        if self.options.get_safe("with_libffi"):
            self.requires("libffi/3.4.2")

        if self.options.get_safe("with_readline"):
            self.requires("readline/8.1.2")

        if self.options.with_gmp:
            self.requires("gmp/6.2.1")

    def validate(self):
        if is_msvc(self) and is_msvc_static_runtime(self):
            # see https://github.com/conan-io/conan-center-index/pull/8644#issuecomment-1068974098
            raise ConanInvalidConfiguration("VS static runtime is not supported")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

        tc = AutotoolsToolchain(self)

        tc.configure_args.append("--disable-install-doc")
        if self.options.shared and not is_msvc(self):
            # Force fPIC
            tc.fpic = True
            if "--enable-shared" not in tc.configure_args:
                tc.configure_args.append("--enable-shared")

        if not self.options.shared and self.options.with_static_linked_ext:
            tc.configure_args.append("--with-static-linked-ext")

        if self.options.with_enable_load_relative:
            tc.configure_args.append("--enable-load-relative")

        # Ruby doesn't respect the --with-gmp-dir for eg. After removal of libgmp-dev on conanio/gcc10 build failed
        opt_dirs = []

        # zlib always True
        tc.configure_args.append(f'--with-zlib-dir={self.dependencies["zlib"].package_path.as_posix()}')
        for dep in ["zlib", "openssl", "libffi", "libyaml", "readline", "gmp"]:
            if self.options.get_safe(f"with_{dep}"):
                root_path = self.dependencies[dep].package_path.as_posix()
                tc.configure_args.append(f"--with-{dep}-dir={root_path}")
                opt_dirs.append(root_path)

        if opt_dirs:
            sep = ";" if self.settings.os == "Windows" else ":"
            tc.configure_args.append(f"--with-opt-dir={sep.join(opt_dirs)}")

        if cross_building(self) and is_apple_os(self):
            apple_arch = to_apple_arch(self)
            if apple_arch:
                tc.configure_args.append(f"--with-arch={apple_arch}")
        if is_msvc(self):
            # this is marked as TODO in https://github.com/conan-io/conan/blob/01f4aecbfe1a49f71f00af8f1b96b9f0174c3aad/conan/tools/gnu/autotoolstoolchain.py#L23
            tc.build_type_flags.append(f"-{msvc_runtime_flag(self)}")

            if Version(self.version) < "3.2.0":
                tc.configure_args.append("--enable-bundled-libffi")
            # https://github.com/conan-io/conan/issues/10338
            # remove after conan 1.45
            if self.settings.build_type in ["Debug", "RelWithDebInfo"]:
                tc.ldflags.append("-debug")
            tc.build_type_flags = [f if f != "-O2" else self._msvc_optflag for f in tc.build_type_flags]

        tc.generate()

        if is_msvc(self):
            vc = VCVars(self)
            vc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "gems", "bundled_gems"), "rbs 2.0.0", "rbs 3.1.0")
        replace_in_file(self, os.path.join(self.source_folder, "gems", "bundled_gems"), "debug 1.4.0", "debug 1.6.3")

    def build(self):
        self._patch_sources()

        autotools = Autotools(self)

        build_script_folder = self.source_folder
        if is_msvc(self):
            self.conf["tools.gnu:make_program"] = "nmake"
            build_script_folder = os.path.join(build_script_folder, "win32")

            if "TMP" in os.environ:  # workaround for TMP in CCI containing both forward and back slashes
                os.environ["TMP"] = os.environ["TMP"].replace("/", "\\")

        autotools.configure(build_script_folder=build_script_folder)
        autotools.make()

    def package(self):
        for file in ["COPYING", "BSDL"]:
            copy(self, pattern=file, src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        autotools = Autotools(self)
        if cross_building(self):
            autotools.make(target="install-local", args=[f"DESTDIR={unix_path(self, self.package_folder)}"])
            autotools.make(target="install-arch", args=[f"DESTDIR={unix_path(self, self.package_folder)}"])
        else:
            autotools.install()

        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, pattern="*.pdb", folder=os.path.join(self.package_folder, "lib"))

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

        config_file = glob.glob(os.path.join(self.package_folder, "include", "**", "ruby", "config.h"), recursive=True)[
            0
        ]
        self.cpp_info.includedirs = [
            os.path.join(self.package_folder, "include", f"ruby-{version}"),
            os.path.dirname(os.path.dirname(config_file)),
        ]
        self.cpp_info.libs = collect_libs(self)
        if is_msvc(self):
            if self.options.shared:
                self.cpp_info.libs = list(filter(lambda l: not l.endswith("-static"), self.cpp_info.libs))
            else:
                self.cpp_info.libs = list(filter(lambda l: l.endswith("-static"), self.cpp_info.libs))

        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["dl", "pthread", "rt", "m", "crypt", "util"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = self._windows_system_libs
        if str(self.settings.compiler) in ("clang", "apple-clang"):
            self.cpp_info.cflags = ["-fdeclspec"]
            self.cpp_info.cxxflags = ["-fdeclspec"]
        if is_apple_os(self):
            self.cpp_info.frameworks = ["CoreFoundation"]

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "Ruby"
        self.cpp_info.names["cmake_find_package_multi"] = "Ruby"
        binpath = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(binpath)
        self.runenv_info.prepend_path("PATH", os.path.join(self.package_folder, "bin"))
