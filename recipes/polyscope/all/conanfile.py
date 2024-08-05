import os
import textwrap

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, save

required_conan_version = ">=1.53.0"


class PolyscopeConan(ConanFile):
    name = "polyscope"
    description = "A viewer for 3D data like meshes and point clouds"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://polyscope.run"
    topics = ("3d", "visualization", "meshes", "point-clouds")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "backend_glfw": [True, False],
        "backend_egl": [True, False],
        "backend_mock": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "backend_glfw": True,
        "backend_egl": True,
        "backend_mock": True,
    }

    def export_sources(self):
        copy(self, "conan_deps.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.backend_egl

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.backend_glfw:
            self.requires("glfw/3.4", transitive_headers=True, transitive_libs=True)
        if self.options.get_safe("backend_egl"):
            self.requires("egl/system", transitive_headers=True, transitive_libs=True)
        if self.options.backend_glfw or self.options.get_safe("backend_egl"):
            self.requires("glad/0.1.36")
        self.requires("glm/cci.20230113", transitive_headers=True, transitive_libs=True)
        self.requires("imgui/1.90.5", transitive_headers=True, transitive_libs=True)
        self.requires("nlohmann_json/3.11.3")
        self.requires("stb/cci.20240531")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_PROJECT_polyscope_INCLUDE"] = "conan_deps.cmake"
        tc.variables["POLYSCOPE_BACKEND_OPENGL3_GLFW"] = self.options.backend_glfw
        tc.variables["POLYSCOPE_BACKEND_OPENGL3_EGL"] = self.options.get_safe("backend_egl")
        tc.variables["POLYSCOPE_BACKEND_OPENGL_MOCK"] = self.options.backend_mock
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("glad", "cmake_target_name", "glad")
        deps.set_property("glfw", "cmake_target_name", "glfw")
        deps.set_property("egl", "cmake_target_name", "EGL")
        deps.set_property("imgui", "cmake_target_name", "imgui")
        deps.generate()

        copy(self, "*",
             os.path.join(self.dependencies["imgui"].package_folder, "res", "bindings"),
             os.path.join(self.source_folder, "include", "backends"))

    def _patch_sources(self):
        # Adjust the implementation of https://github.com/nmwsharp/polyscope/blob/master/deps/stb/CMakeLists.txt
        save(self, os.path.join(self.source_folder, "deps", "stb", "CMakeLists.txt"),
             textwrap.dedent("""\
                add_library(stb OBJECT stb_impl.cpp)
                find_package(stb REQUIRED CONFIG)
                target_link_libraries(stb PUBLIC stb::stb)
                set_target_properties(stb PROPERTIES POSITION_INDEPENDENT_CODE TRUE)
             """))

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        # The project does not define any CMake targets
        self.cpp_info.libs = ["polyscope"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
        elif is_apple_os(self):
            self.cpp_info.frameworks = ["Cocoa", "OpenGL", "CoreVideo", "IOKit"]
