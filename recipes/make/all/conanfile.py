from conan import ConanFile
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, VCVars
import os

required_conan_version = ">=1.53.0"


class MakeConan(ConanFile):
    name = "make"
    description = (
        "GNU Make is a tool which controls the generation of executables and "
        "other non-source files of a program from the program's source files"
    )
    topics = ("make", "build", "makefile")
    homepage = "https://www.gnu.org/software/make/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "GPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        if is_msvc(self):
            vcvars = VCVars(self)
            vcvars.generate()
        if self._settings_build.os != "Windows":
            tc = AutotoolsToolchain(self)
            tc.generate()

    def build(self):
        apply_conandata_patches(self)
        with chdir(self, self.source_folder):
            # README.W32
            if self._settings_build.os == "Windows":
                if is_msvc(self):
                    command = "build_w32.bat --without-guile"
                else:
                    command = "build_w32.bat --without-guile gcc"
            else:
                autotools = Autotools(self)
                autotools.configure()
                command = "./build.sh"
            self.run(command)

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        for make_exe in ("make", "*gnumake.exe"):
            copy(self, make_exe, src=self.source_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        make = os.path.join(self.package_folder, "bin", "gnumake.exe" if self.settings.os == "Windows" else "make")
        self.conf_info.define("tools.gnu:make_program", make)

        # TODO: to remove in conan v2
        self.user_info.make = make
        self.env_info.CONAN_MAKE_PROGRAM = make
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
