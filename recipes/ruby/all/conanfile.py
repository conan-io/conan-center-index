import glob
import os
import re

from conan import ConanFile
from conan.tools.apple import is_apple_os, to_apple_arch

try:
    from conan.tools.cross_building import cross_building
except ImportError:
    from conan.tools.build.cross_building import cross_building

from conan.tools.files import apply_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.microsoft import msvc_runtime_flag, is_msvc
from conans import tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.52.0"


class RubyConan(ConanFile):
    name = "ruby"
    description = "The Ruby Programming Language"
    license = "Ruby"
    topics = ("ruby", "c", "language", "object-oriented", "ruby-language")
    homepage = "https://www.ruby-lang.org"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "patches/**"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": True
    }
    short_paths = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _windows_system_libs(self):
        return ["user32", "advapi32", "shell32", "ws2_32", "iphlpapi", "imagehlp", "shlwapi", "bcrypt"]

    @property
    def _msvc_optflag(self):
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) < "14":
            return "-O2b2xg-"
        else:
            return "-O2sy-"

    def requirements(self):
        self.requires("zlib/1.2.12")
        self.requires("gmp/6.1.2")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1o")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        if is_msvc(self) and msvc_runtime_flag(self).startswith('MT'):
            # see https://github.com/conan-io/conan-center-index/pull/8644#issuecomment-1068974098
            raise ConanInvalidConfiguration("VS static runtime is not supported")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def generate(self):
        td = AutotoolsDeps(self)
        # remove non-existing frameworks dirs, otherwise clang complains
        for m in re.finditer("-F (\S+)", td.vars().get("LDFLAGS")):
            if not os.path.exists(m[1]):
                td.environment.remove("LDFLAGS", f"-F {m[1]}")
        if self.settings.os == "Windows":
            if is_msvc(self):
                td.environment.append("LIBS", [f"{lib}.lib" for lib in self._windows_system_libs])
            else:
                td.environment.append("LDFLAGS", [f"-l{lib}" for lib in self._windows_system_libs])
        td.generate()

        tc = AutotoolsToolchain(self)
        # TODO: removed in conan 1.49
        tc.default_configure_install_args = True

        tc.configure_args.append("--disable-install-doc")
        if self.options.shared and not is_msvc(self):
            # Force fPIC
            tc.fpic = True
            if "--enable-shared" not in tc.configure_args:
                tc.configure_args.append("--enable-shared")

        if cross_building(self) and is_apple_os(self.settings.os):
            apple_arch = to_apple_arch(self.settings.arch)
            if apple_arch:
                tc.configure_args.append(f"--with-arch={apple_arch}")
        if is_msvc(self):
            # this is marked as TODO in https://github.com/conan-io/conan/blob/01f4aecbfe1a49f71f00af8f1b96b9f0174c3aad/conan/tools/gnu/autotoolstoolchain.py#L23
            tc.build_type_flags.append(f"-{msvc_runtime_flag(self)}")
            # https://github.com/conan-io/conan/issues/10338
            # remove after conan 1.45
            if self.settings.build_type in ["Debug", "RelWithDebInfo"]:
                tc.ldflags.append("-debug")
            tc.build_type_flags = [f if f != "-O2" else self._msvc_optflag for f in tc.build_type_flags]

        tc.generate()

    def build(self):
        apply_conandata_patches(self)

        at = Autotools(self)

        build_script_folder = self._source_subfolder
        if is_msvc(self):
            self.conf["tools.gnu:make_program"] = "nmake"
            build_script_folder = os.path.join(build_script_folder, "win32")

            if "TMP" in os.environ:  # workaround for TMP in CCI containing both forward and back slashes
                os.environ["TMP"] = os.environ["TMP"].replace("/", "\\")

        with tools.vcvars(self):
            at.configure(build_script_folder=build_script_folder)
            at.make()

    def package(self):
        for file in ["COPYING", "BSDL"]:
            self.copy(file, dst="licenses", src=self._source_subfolder)

        at = Autotools(self)
        with tools.vcvars(self):
            if cross_building(self):
                at.make(target="install-local")
                at.make(target="install-arch")
            else:
                at.install()

        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.pdb")

    def package_info(self):
        binpath = os.path.join(self.package_folder, "bin")
        self.output.info(f"Adding to PATH: {binpath}")
        self.env_info.PATH.append(binpath)

        version = tools.Version(self.version)
        rubylib = self.cpp_info.components["rubylib"]
        config_file = glob.glob(os.path.join(self.package_folder, "include", "**", "ruby", "config.h"), recursive=True)[0]
        rubylib.includedirs = [
            os.path.join(self.package_folder, "include", f"ruby-{version}"),
            os.path.dirname(os.path.dirname(config_file))
        ]
        rubylib.libs = tools.collect_libs(self)
        if is_msvc(self):
            if self.options.shared:
                rubylib.libs = list(filter(lambda l: not l.endswith("-static"), rubylib.libs))
            else:
                rubylib.libs = list(filter(lambda l: l.endswith("-static"), rubylib.libs))
        rubylib.requires.extend(["zlib::zlib", "gmp::gmp"])
        if self.options.with_openssl:
            rubylib.requires.append("openssl::openssl")
        if self.settings.os in ("FreeBSD", "Linux"):
            rubylib.system_libs = ["dl", "pthread", "rt", "m", "crypt"]
        elif self.settings.os == "Windows":
            rubylib.system_libs = self._windows_system_libs
        if str(self.settings.compiler) in ("clang", "apple-clang"):
            rubylib.cflags = ["-fdeclspec"]
            rubylib.cxxflags = ["-fdeclspec"]
        if tools.is_apple_os(self.settings.os):
            rubylib.frameworks = ["CoreFoundation"]

        self.cpp_info.filenames["cmake_find_package"] = "Ruby"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Ruby"
        self.cpp_info.set_property("cmake_file_name", "Ruby")

        self.cpp_info.names["cmake_find_package"] = "Ruby"
        self.cpp_info.names["cmake_find_package_multi"] = "Ruby"
        self.cpp_info.set_property("cmake_target_name", "Ruby::Ruby")
        self.cpp_info.set_property("pkg_config_aliases", [f"ruby-{version.major}.{version.minor}"])
