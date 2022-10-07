from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, copy, chdir, get
from conans import tools
import os

required_conan_version = ">=1.47.0"

class PSevenZipConan(ConanFile):
    name = "p7zip"
    url = "https://github.com/conan-io/conan-center-index"
    description = "p7zip is a quick port of 7z.exe and 7za.exe (command line version of 7zip, see www.7-zip.org) for Unix"
    license = ("LGPL-2.1", "Unrar")
    homepage = "https://sourceforge.net/projects/p7zip/"
    topics = ("7zip", "zip", "compression", "decompression")
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _make_tool(self):
        return "make" if self.settings.os != "FreeBSD" else "gmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows unsupported - use `7zip` instead")
        if self.settings.arch not in ("armv8", "x86_64"):
            raise ConanInvalidConfiguration("Unsupported architecture")

    def build_requirements(self):
        self.build_requires("make/4.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _build_make(self):
        with chdir(self, os.path.join(self._source_subfolder)):
            command = f"{self._make_tool} -j {tools.cpu_count()}"
            self.run(command)

    def export_sources(self):
        for p in self.conan_data.get("patches").get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def _patch_compiler(self):
        cc = tools.get_env("CC")
        cxx = tools.get_env("CXX")
        optflags = ''
        if tools.is_apple_os(self.settings.os):
            optflags = '-arch ' + tools.to_apple_arch(self.settings.arch)
            if not cc:
                cc = "clang"
            if not cxx:
                cxx = "clang++"
        else:
            if not cc:
                cc = "clang" if self.settings.compiler == "clang" else "gcc"
            if not cxx:
                cxx = "clang++" if self.settings.compiler == "clang" else "g++"
        # Replace the hard-coded compilers instead of using the 40 different Makefile permutations
        tools.replace_in_file(os.path.join(self._source_subfolder, "makefile.machine"),
                              "CC=gcc", f"CC={cc}")
        tools.replace_in_file(os.path.join(self._source_subfolder, "makefile.machine"),
                              "CXX=g++", f"CXX={cxx}")
        # Manually modify the -O flag here based on the build type
        optflags += " -O2" if self.settings.build_type == "Release" else " -O0"
        # Silence the warning about `-s` not being valid on clang
        if cc != "clang":
            optflags += ' -s'
        tools.replace_in_file(os.path.join(self._source_subfolder, "makefile.machine"),
                            "OPTFLAGS=-O -s", "OPTFLAGS=" + optflags)

    def _patch_sources(self):
        apply_conandata_patches(self)
        self._patch_compiler()

    def build(self):
        self._patch_sources()
        self._build_make()

    def package(self):
        self.copy("DOC/License.txt", src=self._source_subfolder, dst="licenses", keep_path=False)
        self.copy("DOC/unRarLicense.txt", src=self._source_subfolder, dst="licenses", keep_path=False)
        self.copy("7za", src=os.path.join(self._source_subfolder, "bin"), dst="bin", keep_path=False)

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.path.append(bin_path)
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
