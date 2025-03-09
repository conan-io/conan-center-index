from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
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
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

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
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        if is_msvc(self):
            vcvars = VCVars(self)
            vcvars.generate()
        if self.settings_build.os != "Windows":
            tc = AutotoolsToolchain(self)
            tc.generate()

    def build(self):
        if self.settings_build.os == "Windows":
            # README.W32
            if is_msvc(self):
                self.run("build_w32.bat --without-guile", cwd=self.source_folder)
            else:
                self.run("build_w32.bat --without-guile gcc", cwd=self.source_folder)
        else:
            autotools = Autotools(self)
            autotools.configure()
            self.run("./build.sh")

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        for make_exe in ("make", "*gnumake.exe"):
            src = self.source_folder if self.settings_build.os == "Windows" else self.build_folder
            copy(self, make_exe, src, os.path.join(self.package_folder, "bin"), keep_path=False)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        make = os.path.join(self.package_folder, "bin", "gnumake.exe" if self.settings.os == "Windows" else "make")
        self.conf_info.define("tools.gnu:make_program", make)
