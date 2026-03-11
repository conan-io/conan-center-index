import os

from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rename, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=2.0"


class AutomakeConan(ConanFile):
    name = "automake"
    description = (
        "Automake is a tool for automatically generating Makefile.in files"
        " compliant with the GNU Coding Standards."
    )
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/automake/"
    topics = ("autotools", "configure", "build")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("autoconf/2.71")
        # automake requires perl-Thread-Queue package

    def package_id(self):
        del self.info.settings.arch
        del self.info.settings.compiler
        del self.info.settings.build_type

    def build_requirements(self):
        self.tool_requires("autoconf/2.71")
        if self.settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if self.settings.os == "Windows":
            # tracing using m4 on Windows returns Windows paths => use cygpath to convert to unix paths
            ac_local_in = os.path.join(self.source_folder, "bin", "aclocal.in")
            replace_in_file(self, ac_local_in,
                                "          $map_traced_defs{$arg1} = $file;",
                                "          $file = `cygpath -u $file`;\n"
                                "          $file =~ s/^\\s+|\\s+$//g;\n"
                                "          $map_traced_defs{$arg1} = $file;")
            # handle relative paths during aclocal.m4 creation
            replace_in_file(self, ac_local_in, "$map{$m} eq $map_traced_defs{$m}",
                                "abs_path($map{$m}) eq abs_path($map_traced_defs{$m})")

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()
        copy(self, "COPYING*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        rmdir(self, os.path.join(self.package_folder, "share", "info"))
        rmdir(self, os.path.join(self.package_folder, "share", "man"))
        rmdir(self, os.path.join(self.package_folder, "share", "doc"))

        if self.settings.os == "Windows":
            # TODO: consider whether the following is still necessary on Windows
            binpath = os.path.join(self.package_folder, "bin")
            for filename in os.listdir(binpath):
                fullpath = os.path.join(binpath, filename)
                if not os.path.isfile(fullpath):
                    continue
                rename(self, fullpath, fullpath + ".exe")

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.frameworkdirs = []

        # For consumers with new integrations (Conan 1 and 2 compatible):
        ver = Version(self.version)
        automake_helper_scripts_dir = os.path.join(self.package_folder, "share", f"automake-{ver.major}.{ver.minor}")
        compile_wrapper = os.path.join(automake_helper_scripts_dir, "compile")
        lib_wrapper = os.path.join(automake_helper_scripts_dir, "ar-lib")
        self.conf_info.define("user.automake:compile-wrapper", compile_wrapper)
        self.conf_info.define("user.automake:lib-wrapper", lib_wrapper)
