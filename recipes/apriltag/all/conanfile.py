from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, replace_in_file, save
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
        if is_msvc(self) and Version(self.version) < "3.3.0":
            self.requires("pthreads4w/3.0.0", transitive_headers=True)

    def validate(self):
        if is_msvc(self) and self.settings.build_type == "Debug":
            # segfault in test package...
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support Debug with msvc yet")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_EXAMPLES"] = False
        if Version(self.version) >= "3.1.4":
            tc.variables["BUILD_PYTHON_WRAPPER"] = False
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        if self.settings.os == "Windows":
            tc.preprocessor_definitions["NOMINMAX"] = ""
        tc.generate()
        if is_msvc(self):
            deps = CMakeDeps(self)
            deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Fix DLL installation
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}",
                        "ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}\n"
                        "RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}")
        # Skip the building and installation of examples
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "# Examples", "return()")

    def build(self):
        self._patch_sources()
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
        suffix = ""
        if self.settings.build_type == "Debug" and Version(self.version) >= "3.2.0":
            suffix = "d"
        self.cpp_info.libs = ["apriltag" + suffix]
        self.cpp_info.includedirs.append(os.path.join("include", "apriltag"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["winmm"]
            self.cpp_info.defines.append("NOMINMAX")
