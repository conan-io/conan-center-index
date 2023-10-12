from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class QGeoViewConan(ConanFile):
    name = "qgeoview"
    description = "QGeoView is a Qt / C ++ widget for visualizing geographic data. "
    license = "LGPL-3.0"
    topics = ("geo", "geospatial", "qt")
    homepage = "https://github.com/AmonRaNet/QGeoView"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("qt/6.5.3")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            min_cppstd = "11" if Version(self.dependencies["qt"].ref.version) < "6.0.0" else "17"
            check_min_cppstd(self, min_cppstd)
        if not (self.dependencies["qt"].options.gui and self.dependencies["qt"].options.widgets):
            raise ConanInvalidConfiguration(f"{self.ref} requires qt gui and widgets")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["QT_VERSION"] = self.dependencies["qt"].ref.version
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        
    def package_info(self):
        self.cpp_info.libs = ["qgeoview"]
        self.cpp_info.libdirs = ['lib', os.path.join('lib','static')]  # Directories where libraries can be found
        self.cpp_info.requires = ["qt::qtCore", "qt::qtGui", "qt::qtWidgets", "qt::qtNetwork"]
