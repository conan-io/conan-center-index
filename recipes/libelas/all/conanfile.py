import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import copy, get, rm, download, load, save, export_conandata_patches, apply_conandata_patches

required_conan_version = ">=1.53.0"


class LibelasConan(ConanFile):
    name = "libelas"
    description = "LIBELAS is a C++ library for computing disparity maps from rectified graylevel stereo pairs"
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.cvlibs.net/software/libelas/"
    topics = ("computer-vision", "stereo-matching", "disparity", "depth")

    package_type = "library"
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
        export_conandata_patches(self)
        copy(self, "CMakeLists.txt", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("llvm-openmp/17.0.6")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 98)
        if self.settings.arch not in ["x86", "x86_64"]:
            raise ConanInvalidConfiguration("Only x86 and x86_64 architectures are supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["sources"], strip_root=True)
        download(self, **self.conan_data["sources"][self.version]["license"], filename="README.TXT")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["USE_SSE3"] = self.settings.arch in ["x86", "x86_64"]
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _read_license(self):
        content = load(self, os.path.join(self.source_folder, "README.TXT"))
        return "\n".join(content.splitlines()[:46])

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._read_license())
        cmake = CMake(self)
        cmake.install()
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["elas"]
