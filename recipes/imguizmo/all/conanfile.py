import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class ImGuizmoConan(ConanFile):
    name = "imguizmo"
    description = "Immediate mode 3D gizmo for scene editing and other controls based on Dear Imgui"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/CedricGuillemet/ImGuizmo"
    topics = ("imgui", "3d", "graphics", "guizmo")

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
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("imgui/1.90.5", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.preprocessor_definitions["IMGUI_DEFINE_MATH_OPERATORS"] = ""
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        if self.version == "1.83" and Version(self.dependencies["imgui"].ref.version) >= "1.89.4":
            # Related to a breaking change: https://github.com/ocornut/imgui/blob/master/docs/CHANGELOG.txt#L912
            # Redirection: ImDrawList::AddBezierCurve() -> use ImDrawList::AddBezierCubic()
            replace_in_file(self, os.path.join(self.source_folder, "GraphEditor.cpp"),
                            "AddBezierCurve", "AddBezierCubic")
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.source_path.parent)
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["imguizmo"]
