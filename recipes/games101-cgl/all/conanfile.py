from conan import ConanFile
from conan.tools.files import get, copy, rmdir, rm
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.55.0"

class Games101CglConan(ConanFile):
    name = "games101-cgl"
    description = "The package is for Games101's homework8 subproject"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/endingly/games101-cgl"
    topics = ("games101", "graphics")
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

    @property
    def _min_cppstd(self):
        return 11

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("freetype/2.13.2")
        self.requires("glew/2.2.0", transitive_headers=True)
        self.requires("glfw/3.4", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.25 <4.0.0]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        suffix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = ["CGL" + suffix]

        self.cpp_info.set_property("cmake_file_name", "games101-cgl")
        self.cpp_info.set_property("cmake_target_name", "games101-cgl::games101-cgl")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "games101-cgl"
        self.cpp_info.filenames["cmake_find_package_multi"] = "games101-cgl"
        self.cpp_info.names["cmake_find_package"] = "games101-cgl"
        self.cpp_info.names["cmake_find_package_multi"] = "games101-cgl"
