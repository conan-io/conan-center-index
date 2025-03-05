import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, chdir
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class PSevenZipConan(ConanFile):
    name = "p7zip"
    url = "https://github.com/conan-io/conan-center-index"
    description = "p7zip is a quick port of 7z.exe and 7za.exe (command line version of 7zip, see www.7-zip.org) for Unix"
    license = ("LGPL-2.1", "Unrar")
    homepage = "https://sourceforge.net/projects/p7zip/"
    topics = ("7zip", "zip", "compression", "decompression")
    settings = "os", "arch", "compiler", "build_type"
    package_type = "application"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def validate(self):
        if self.info.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on Windows - use `7zip` instead")
        if self.info.settings.arch not in ("armv8", "x86_64"):
            raise ConanInvalidConfiguration(f"{self.ref} is only supported by x86_64 and armv8")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    @property
    def _compiler_executables(self):
        compiler = str(self.settings.compiler)
        cc = "clang" if "clang" in compiler else compiler
        cxx = "clang++" if "clang" in compiler else compiler
        if compiler == "gcc":
            cxx = "g++"
        tc_vars = AutotoolsToolchain(self).vars()
        cc = tc_vars.get("CC", cc)
        cxx = tc_vars.get("CXX", cxx)
        return cc, cxx

    def generate(self):
        cc, cxx = self._compiler_executables
        tc = AutotoolsToolchain(self)
        tc_vars = tc.vars()
        tc.make_args.extend([
            f"CC={cc}",
            f"CXX={cxx}",
            f"OPTFLAGS={tc_vars['CFLAGS']}",
        ])
        tc.generate()

    def build(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make()

    def package(self):
        copy(self, "License.txt", src=os.path.join(self.source_folder, "DOC"), dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "unRarLicense.txt", src=os.path.join(self.source_folder, "DOC"), dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "7za", src=os.path.join(self.source_folder, "bin"), dst=os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
