from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc, check_min_vs
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.53.0"


class LinuxDeployConan(ConanFile):
    name = "linuxdeploy"
    homepage = "https://github.com/linuxdeploy/linuxdeploy"
    description = "A tool to generate AppDirs"
    topics = ("appdir", "appimage", "deploy")
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

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "7",
            "apple-clang": "11",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def generate(self):
        tc = CMakeDeps(self)
        tc.generate()
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["GIT_COMMIT"] = "0000000" # Expects short hash
        tc.generate()

    def layout(self):
        cmake_layout(self, src_folder="src")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
    
    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.options["cimg"].enable_png = True # Enable at least PNGs by default, maybe enable_magick?

    def requirements(self):
        self.requires("xorg/system")
        self.requires("patchelf/0.13")
        self.requires("taywee-args/6.4.4")
        self.requires("cimg/3.2.0")

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, 17)
        check_min_vs(self, 191)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(
                str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++17, which your compiler does not support."
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["source"],
            destination=self.source_folder, strip_root=True)
        get(self, **self.conan_data["sources"][self.version]["linuxdeploy-desktopfile-source"],
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
