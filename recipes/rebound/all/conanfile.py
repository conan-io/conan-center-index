from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import Environment
from conan.tools.files import chdir, copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
import os


required_conan_version = ">=1.54.0"


class ReboundConan(ConanFile):
    name = "rebound"
    description = "REBOUND is an N-body integrator, i.e. a software package that can integrate the motion of particles under the influence of gravity."
    license = "GPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/hannorein/rebound"
    topics = ("physics", "simulation", "n-body", "gravity", "integrator")
    package_type = "shared-library"
    settings = "os", "arch", "compiler"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def configure(self):
        # for plain C projects only
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

        # If Visual Studio is supported
        if is_msvc(self):
            env = Environment()
            # get compile & ar-lib from automake (or eventually lib source code if available)
            # it's not always required to wrap CC, CXX & AR with these scripts, it depends on how much love was put in
            # upstream build files
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} \"lib -nologo\"")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_msvc")

    def build(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make(target="librebound")

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "librebound.so", os.path.join(self.source_folder, "src"), os.path.join(self.package_folder, "lib"))

        copy(self, "*.h", os.path.join(self.source_folder, "src"), os.path.join(self.package_folder, "include"))

        # some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        # In shared lib/executable files, autotools set install_name (macOS) to lib dir absolute path instead of @rpath, it's not relocatable, so fix it
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["rebound"]

