from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
import os

required_conan_version = ">=2.0.0"

class PackageConan(ConanFile):
    name = "optick"
    description = "Optick is a super-lightweight C++ profiler for Games"
    license = "MIT"
    url = "https://github.com/bombomby/optick"
    homepage = "https://github.com/bombomby/optick"
    topics = ("profiler", "games")
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {}
    default_options = {}

    @property
    def _min_cppstd(self):
        return 11

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        pass

    def configure(self):
        pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        pass

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        if not is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} can be built only by Visual Studio and msvc.")

    def build_requirements(self):
        pass

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        
        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)

        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["OptickCore" + ("d" if self.settings.build_type == "Debug" else "")]

        self.cpp_info.set_property("cmake_file_name", "Optick")
        self.cpp_info.set_property("cmake_target_name", "Optick::OptickCore")
