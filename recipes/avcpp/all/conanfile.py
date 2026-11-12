from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir
import os

required_conan_version = ">=2.1"


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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("ffmpeg/[>=6.1 <9]", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 17)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.19]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

        # Fix issue with install targets
        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"),
                        "install(TARGETS ${AV_TARGETS} FFmpeg",
                        'install(TARGETS ${AV_TARGETS}')

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.cache_variables["AV_ENABLE_SHARED"] = self.options.shared
        tc.cache_variables["AV_ENABLE_STATIC"] = not self.options.shared
        tc.cache_variables["AV_BUILD_EXAMPLES"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("ffmpeg", "cmake_file_name", "FFmpeg")
        deps.set_property("ffmpeg", "cmake_target_name", "FFmpeg::FFmpeg")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):

        self.cpp_info.set_property("cmake_file_name", "avcpp")
        self.cpp_info.set_property("cmake_target_name", "avcpp::avcpp")
        if not self.options.shared:
            # upstream CMakeLists.txt uses "avcpp-static" as target name only
            # when both shared and static libraries are built, we keep this for compatibility
            self.cpp_info.set_property("cmake_target_aliases", ["avcpp::avcpp-static"])
        self.cpp_info.libs = ["avcpp"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["mvec"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["mfplat"]
