from conan import ConanFile
from conans import AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc, VCVars
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.microsoft import is_msvc
from conans.client.tools.env import no_op
import os

required_conan_version = ">=1.52.0"

class MakeConan(ConanFile):
    name = "make"
    description = "GNU Make is a tool which controls the generation of executables and other non-source files of a program from the program's source files"
    topics = ("conan", "make", "build", "makefile")
    homepage = "https://www.gnu.org/software/make/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "GPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def package_id(self):
        del self.info.settings.compiler

    def build(self):
        # README.W32
        if is_msvc(self):
            if self.settings.compiler == "Visual Studio":
                command = "build_w32.bat --without-guile"
            else:
                command = "build_w32.bat --without-guile gcc"
        else:
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure()
            command = "./build.sh"
        with VCVars(self) if is_msvc(self) else no_op():
            self.run(command)

    def package(self):
        self.copy(pattern="COPYING", dst="licenses")
        self.copy(pattern="make", dst="bin", keep_path=False)
        self.copy(pattern="*gnumake.exe", dst="bin", keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = []

        make = os.path.join(self.package_folder, "bin", "gnumake.exe" if self.settings.os == "Windows" else "make")

        self.user_info.make = make

        self.output.info('Creating CONAN_MAKE_PROGRAM environment variable: %s' % make)
        self.env_info.CONAN_MAKE_PROGRAM = make
        self.env_info.CMAKE_MAKE_PROGRAM = make
