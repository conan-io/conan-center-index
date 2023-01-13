import os

from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"


class AutomakeConan(ConanFile):
    name = "automake"
    package_type = "application"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/automake/"
    description = "Automake is a tool for automatically generating Makefile.in files compliant with the GNU Coding Standards."
    topics = ("conan", "automake", "configure", "build")
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _version_major_minor(self):
        [major, minor, _] = self.version.split(".", 2)
        return '{}.{}'.format(major, minor)

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("autoconf/2.71")
        # automake requires perl-Thread-Queue package

    def build_requirements(self):
        if hasattr(self, "settings_build"):
            self.build_requires("autoconf/2.71")
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", check_type=str):
            self.win_bash = True
            self.build_requires("msys2/cci.latest")

    def package_id(self):
        del self.info.settings.arch
        del self.info.settings.compiler
        del self.info.settings.build_type

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    @property
    def _datarootdir(self):
        return os.path.join(self.package_folder, "res")

    @property
    def _automake_libdir(self):
        return os.path.join(self._datarootdir, "automake-{}".format(self._version_major_minor))

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--datarootdir=${prefix}/res",
        ])

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
        copy(self, "COPYING*", src=self.source_folder, dst=os.path.join(self.package_folder,"licenses"))

        rmdir(self, os.path.join(self._datarootdir, "info"))
        rmdir(self, os.path.join(self._datarootdir, "man"))
        rmdir(self, os.path.join(self._datarootdir, "doc"))

        # TODO: consider whether the following is still necessary on Windows
        if self.settings.os == "Windows":
            binpath = os.path.join(self.package_folder, "bin")
            for filename in os.listdir(binpath):
                fullpath = os.path.join(binpath, filename)
                if not os.path.isfile(fullpath):
                    continue
                os.rename(fullpath, fullpath + ".exe")

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

        # For consumers with new integrations (Conan 1 and 2 compatible):
        compile_wrapper = os.path.join(self._automake_libdir, "compile")
        lib_wrapper = os.path.join(self._automake_libdir, "ar-lib")
        self.conf_info.define("user.automake:compile-wrapper", compile_wrapper)
        self.conf_info.define("user.automake:lib-wrapper", lib_wrapper)

        # For legacy Conan 1.x consumers only:
        self.user_info.compile = compile_wrapper
        self.user_info.ar_lib = lib_wrapper
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable:: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
