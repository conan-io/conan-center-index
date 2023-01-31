from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.layout import cmake_layout
from conan.tools.scm import Version, Git
import os

required_conan_version = ">=1.53.0"


class LinuxDeployConan(ConanFile):
    name = "linuxdeploy"
    homepage = "https://github.com/linuxdeploy/linuxdeploy"
    description = "A safe and fast alternative to printf and IOStreams."
    topics = ("format", "iostream", "printf")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False]
    }

    default_options = {
        "fPIC": True,
        "shared": False
    }

    def init(self):
        self.build_hash = Git(self).get_commit()

    def export_sources(self):
        export_conandata_patches(self)

    def generate(self):
        tc = CMakeDeps(self)
        tc.generate()
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["GIT_COMMIT"] = self.build_hash[:7] # Expects short hash
        tc.generate()

    def layout(self):
        cmake_layout(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
    
    def configure(self):
        self.options["cimg"].enable_png = True # Enable at least PNGs by default, maybe enable_magick?

    def requirements(self):
        self.requires("xorg/system")
        self.requires("patchelf/0.13")
        self.requires("taywee-args/6.4.4")
        self.requires("cimg/3.2.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)
        get(self, **self.conan_data["linuxdeploy-desktopfile"][self.version],
            destination=os.path.join(self.source_folder, "lib", "linuxdeploy-desktopfile"), strip_root=True)

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "res"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["linuxdeploy_core", "linuxdeploy_desktopfile"]
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin")) # Does this need to be explicit?
