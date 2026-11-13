from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain, CMakeDeps
from conan.tools.files import get, apply_conandata_patches, export_conandata_patches, copy
import os


class Nfiq2Conan(ConanFile):
    name = "nfiq2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/usnistgov/nfiq2"
    topics = ("NIST", "fingerprint", "biometrics", "quality")
    license = "NIST-PD"
    description = ("NIST Fingerprint Image Quality 2 open source software that links "
                     "fingerprint image quality to operational recognition performance.")
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}
    package_type = "static-library"

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("opencv/4.10.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["nfiq2"], strip_root=True)
        get(self, **self.conan_data["sources"][self.version]["fingerjetfxose"],
            destination=os.path.join(self.source_folder, "fingerjetfxose"), strip_root=True)
        get(self, **self.conan_data["sources"][self.version]["digestpp"],
            destination=os.path.join(self.source_folder, "digestpp"), strip_root=True)
        copy(self, "CMakeLists.txt", src=self.export_sources_folder, dst=self.source_folder)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["nfiq2", "FRFXLL_static"]
        self.cpp_info.set_property("cmake_file_name", "nfiq2")
        self.cpp_info.set_property("cmake_target_name", "nfiq2::nfiq2")
        self.cpp_info.requires = ["opencv::opencv"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "dl"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
