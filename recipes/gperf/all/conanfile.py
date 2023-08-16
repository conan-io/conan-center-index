from conan import ConanFile
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, check_min_vs, unix_path
import os

required_conan_version = ">=1.57.0"


class GperfConan(ConanFile):
    name = "gperf"
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/gperf"
    description = "GNU gperf is a perfect hash function generator"
    topics = ("hash-generator", "hash")

    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")
        self.folders.build = self.folders.source

    def package_id(self):
        del self.info.settings.compiler

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        if is_msvc(self) and check_min_vs(self, "180", raise_invalid=False):
            tc.extra_cflags.append("-FS")
            tc.extra_cxxflags.append("-FS")
        tc.generate()

        if is_msvc(self):
            env = Environment()
            compile_wrapper = unix_path(self, os.path.join(self.source_folder, "build-aux", "compile"))
            ar_wrapper = unix_path(self, os.path.join(self.source_folder, "build-aux", "ar-lib"))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.append("CPPFLAGS", "-D_WIN32_WINNT=_WIN32_WINNT_WIN8")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} \"lib -nologo\"")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            
            #Prevent msys2 from performing erroneous path conversions for C++ files
            # when invoking cl.exe as this is already handled by the compile wrapper.
            env.define("MSYS2_ARG_CONV_EXCL", "-Tp") 
            env.vars(self).save_script("conanbuild_gperf_msvc")

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        with chdir(self, self.source_folder):
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        with chdir(self, self.source_folder):
            # TODO: replace by autotools.install() once https://github.com/conan-io/conan/issues/12153 fixed
            autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
