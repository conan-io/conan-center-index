from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class ApriltagConan(ConanFile):
    name = "apriltag"
    description = ("AprilTag is a visual fiducial system, useful for a wide variety of tasks \
                    including augmented reality, robotics, and camera calibration")
    homepage = "https://april.eecs.umich.edu/software/apriltag"
    topics = ("robotics",)
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if is_msvc(self):
            self.requires("pthreads4w/3.0.0", transitive_headers=True)

    def validate(self):
        if is_msvc(self) and self.settings.build_type == "Debug":
            # segfault in test package...
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support Debug with msvc yet")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) >= "3.1.4":
            tc.variables["BUILD_PYTHON_WRAPPER"] = False
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()
        if is_msvc(self):
            deps = CMakeDeps(self)
            deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "apriltag")
        self.cpp_info.set_property("cmake_target_name", "apriltag::apriltag")
        self.cpp_info.set_property("pkg_config_name", "apriltag")
        self.cpp_info.libs = ["apriltag"]
        self.cpp_info.includedirs.append(os.path.join("include", "apriltag"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["winmm"]
