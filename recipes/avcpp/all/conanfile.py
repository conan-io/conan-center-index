from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class AvcppConan(ConanFile):
    name = "avcpp"
    description = "C++ wrapper for FFmpeg"
    license = "LGPL-2.1", "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/h4tr3d/avcpp/"
    topics = ("ffmpeg", "cpp")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
    }

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12.0",
            "Visual Studio": "15",
            "msvc": "191",
        }

    def export_sources(self):
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
        self.requires("ffmpeg/6.1", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        if Version(self.version) >= "2.2.0":
            self.tool_requires("cmake/[>=3.19 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.variables["AV_ENABLE_SHARED"] = self.options.shared
        tc.variables["AV_ENABLE_STATIC"] = not self.options.shared
        tc.variables["AV_BUILD_EXAMPLES"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        target_name = "avcpp" if self.options.shared else "avcpp-static"

        self.cpp_info.set_property("cmake_file_name", "avcpp")
        self.cpp_info.set_property("cmake_target_name", f"avcpp::{target_name}")

        self.cpp_info.components["AvCpp"].names["cmake_find_package"] = target_name
        self.cpp_info.components["AvCpp"].names["cmake_find_package_multi"] = target_name
        self.cpp_info.components["AvCpp"].set_property("cmake_target_name", f"avcpp::{target_name}")
        self.cpp_info.components["AvCpp"].libs = ["avcpp", ]
        self.cpp_info.components["AvCpp"].requires = ["ffmpeg::ffmpeg", ]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["AvCpp"].system_libs = ["mvec"]
        if self.settings.os == "Windows":
            self.cpp_info.components["AvCpp"].system_libs = ["mfplat"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "avcpp"
        self.cpp_info.filenames["cmake_find_package_multi"] = "avcpp"
        self.cpp_info.names["cmake_find_package"] = "avcpp"
        self.cpp_info.names["cmake_find_package_multi"] = "avcpp"
