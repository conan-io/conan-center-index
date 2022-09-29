from conan import ConanFile
from conans import AutoToolsBuildEnvironment
from conan.tools.microsoft import is_msvc, VCVars
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, chdir
import os

required_conan_version = ">=1.52.0"

class MakeConan(ConanFile):
    name = "make"
    description = "GNU Make is a tool which controls the generation of executables and other non-source files of a program from the program's source files"
    topics = ("make", "build", "makefile")
    homepage = "https://www.gnu.org/software/make/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "GPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def package_id(self):
        del self.info.settings.compiler

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        with chdir(self, self._source_subfolder):
            self._patch_sources()
            # README.W32
            if is_msvc(self):
                if is_msvc(self):
                    command = "build_w32.bat --without-guile"
                else:
                    command = "build_w32.bat --without-guile gcc"
            else:
                env_build = AutoToolsBuildEnvironment(self)
                env_build.configure()
                command = "./build.sh"
            self.run(command)

    def package(self):
        self.copy(pattern="COPYING", src=self._source_subfolder, dst="licenses")
        self.copy(pattern="make", src=self._source_subfolder, dst="bin", keep_path=False)
        self.copy(pattern="*gnumake.exe", src=self._source_subfolder, dst="bin", keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = []

        make = os.path.join(self.package_folder, "bin", "gnumake.exe" if self.settings.os == "Windows" else "make")

        self.user_info.make = make

        self.output.info('Creating CONAN_MAKE_PROGRAM environment variable: %s' % make)
        self.env_info.CONAN_MAKE_PROGRAM = make
        self.env_info.CMAKE_MAKE_PROGRAM = make
