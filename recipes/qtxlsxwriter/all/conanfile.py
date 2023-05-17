from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, download, export_conandata_patches, get
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class QtXlsxWriterConan(ConanFile):
    name = "qtxlsxwriter"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dbzhang800/QtXlsxWriter"
    description = ".xlsx file reader and writer for Qt5"
    topics = ("excel", "xlsx")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("qt/5.15.7")

    def validate(self):
        if not self.dependencies["qt"].options.gui:
            raise ConanInvalidConfiguration(f"{self.ref} requires qt gui")
        # FIXME: to remove once https://github.com/conan-io/conan/issues/11385 fixed
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration(f"{self.ref} recipe does not support cross-compilation yet")

    def build_requirements(self):
        if hasattr(self, "settings_build") and cross_building(self):
            self.tool_requires("qt/5.15.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["source"],
            destination=self.source_folder, strip_root=True)
        download(self, **self.conan_data["sources"][self.version]["license"], filename="LICENSE")

    def generate(self):
        if hasattr(self, "settings_build") and cross_building(self):
            env = VirtualBuildEnv(self)
            env.generate()
        else:
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = CMakeToolchain(self)
        tc.variables["QTXLSXWRITER_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["QT_VERSION_MAJOR"] = str(Version(self.dependencies["qt"].ref.version).major)
        tc.variables["QT_ROOT"] = self.dependencies["qt"].package_folder.replace("\\", "/")
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["qtxlsxwriter"]
        if not self.options.shared:
            self.cpp_info.defines = ["QTXLSX_STATIC"]
        self.cpp_info.requires = ["qt::qtCore", "qt::qtGui"]
