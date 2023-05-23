from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, replace_in_file, chdir
from conan.tools.layout import basic_layout
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.apple import is_apple_os, to_apple_arch
import os


required_conan_version = ">=1.52.0"


class PSevenZipConan(ConanFile):
    name = "p7zip"
    url = "https://github.com/conan-io/conan-center-index"
    description = "p7zip is a quick port of 7z.exe and 7za.exe (command line version of 7zip, see www.7-zip.org) for Unix"
    license = ("LGPL-2.1", "Unrar")
    homepage = "https://sourceforge.net/projects/p7zip/"
    topics = ("7zip", "zip", "compression", "decompression")
    settings = "os", "arch", "compiler", "build_type"

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
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def _patch_compiler(self):
        optflags = ''
        if is_apple_os(self):
            optflags = '-arch ' + to_apple_arch(self)
        cc = "clang" if "clang" in str(self.settings.compiler) else str(self.settings.compiler)
        cxx = "clang++" if "clang" in str(self.settings.compiler) else str(self.settings.compiler)
        if self.settings.compiler == "gcc":
            cxx = "g++"
        # Replace the hard-coded compilers instead of using the 40 different Makefile permutations
        replace_in_file(self, os.path.join(self.source_folder, "makefile.machine"),
                              "CC=gcc", f"CC={cc}")
        replace_in_file(self, os.path.join(self.source_folder, "makefile.machine"),
                              "CXX=g++", f"CXX={cxx}")
        # Manually modify the -O flag here based on the build type
        optflags += " -O2" if self.settings.build_type == "Release" else " -O0"
        # Silence the warning about `-s` not being valid on clang
        if cc != "clang":
            optflags += ' -s'
        replace_in_file(self, os.path.join(self.source_folder, "makefile.machine"),
                            "OPTFLAGS=-O -s", "OPTFLAGS=" + optflags)

    def _patch_sources(self):
        apply_conandata_patches(self)
        self._patch_compiler()

    def build(self):
        self._patch_sources()
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make()

    def package(self):
        copy(self, "License.txt", src=os.path.join(self.source_folder, "DOC"), dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "unRarLicense.txt", src=os.path.join(self.source_folder, "DOC"), dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "7za", src=os.path.join(self.source_folder, "bin"), dst=os.path.join(self.package_folder, "bin"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)

        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
