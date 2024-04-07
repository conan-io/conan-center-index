import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake
from conan.tools.files import get, copy, download, export_conandata_patches, apply_conandata_patches
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.54.0"

class F2cConan(ConanFile):
    name = "f2c"
    description = "Fortran 77 to C/C++ translator and compiler wrapper"
    license = "SMLNJ"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://netlib.org/f2c/"
    topics = ("fortran", "translator", "tool")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fc_wrapper": [True, False],
    }
    default_options = {
        "fc_wrapper": True,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler
        del self.info.options.fc_wrapper

    def requirements(self):
        self.requires("libf2c/20240130", transitive_headers=True, transitive_libs=True, run=True)

    @staticmethod
    def _chmod_plus_x(name):
        if os.name == "posix":
            os.chmod(name, os.stat(name).st_mode | 0o111)

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["f2c"], strip_root=True)
        download(self, **self.conan_data["sources"][self.version]["fc"], filename="fc")
        self._chmod_plus_x("fc")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "Notice", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        copy(self, "fc", self.source_folder, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        f2c_path = os.path.join(self.package_folder, "bin", "f2c")
        self.buildenv_info.define_path("F2C", f2c_path)

        if self.options.fc_wrapper:
            fc_path = os.path.join(self.package_folder, "bin", "fc")
            libf2c = self.dependencies.host["libf2c"].cpp_info
            if is_msvc(self):
                cflags = f"-I{libf2c.includedir} -link /LIBPATH:{libf2c.libdir} f2c.lib"
            else:
                cflags = f"-I{libf2c.includedir} -L{libf2c.libdir} -lf2c"
            self.buildenv_info.define_path("FC", fc_path)
            self.buildenv_info.define("CFLAGSF2C", cflags)
            self.env_info.FC = fc_path
            self.env_info.CFLAGSF2C = cflags

        # TODO: Legacy, to be removed on Conan 2.0
        bin_folder = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_folder)
        self.env_info.F2C = f2c_path
