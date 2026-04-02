from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os


required_conan_version = ">=2.0.9"


class PackageConan(ConanFile):
    name = "videoviewer"
    description = "Video viewer that creates an OpenGL (Core Profile 4.1) window to display incoming video data."
    license = "Apache-2.0"
    url = "https://github.com/deltacasttv/video-viewer"
    homepage = "https://github.com/deltacasttv/video-viewer"
    topics = ("video", "opengl", "viewer")
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

    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("glfw/[>=3.4 <4]")
        self.requires("glm/cci.20230113")

    def validate(self):
        check_min_cppstd(self, 14)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        if is_msvc(self):
            tc.cache_variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "include", "gl3w"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["video-viewer"]
        self.cpp_info.set_property("cmake_module_file_name", "videoviewer")
        self.cpp_info.set_property("cmake_module_target_name", "videoviewer::videoviewer")
        self.cpp_info.set_property("cmake_file_name", "videoviewer")
        self.cpp_info.set_property("cmake_target_name", "videoviewer::videoviewer")
        self.cpp_info.set_property("pkg_config_name", "videoviewer")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")
