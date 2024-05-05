from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, replace_in_file
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.54"

class ImplotConan(ConanFile):
    name = "implot"
    description = "Advanced 2D Plotting for Dear ImGui"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/epezent/implot"
    topics = ("imgui", "plot", "graphics", )
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
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        if Version(self.version) >= "0.14":
            self.requires("imgui/1.90.5", transitive_headers=True)
        elif Version(self.version) >= "0.13":
            # imgui 1.89 renamed ImGuiKeyModFlags_* to  ImGuiModFlags_*
            self.requires("imgui/1.88", transitive_headers=True)
        else:
            self.requires("imgui/1.86", transitive_headers=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if Version(self.version) < "0.13" and is_msvc(self) and self.dependencies["imgui"].options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support shared imgui.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["IMPLOT_SRC_DIR"] = self.source_folder.replace("\\", "/")
        if Version(self.version) < "0.16":
            # Set in code since v0.16 https://github.com/epezent/implot/commit/33c5a965f55f80057f197257d1d1cdb06523e963
            tc.preprocessor_definitions["IMGUI_DEFINE_MATH_OPERATORS"] = ""
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        if Version(self.version) == "0.14" and Version(self.dependencies["imgui"].ref.version) >= "1.89.7":
            # https://github.com/ocornut/imgui/commit/51f564eea6333bae9242f40c983a3e29d119a9c2
            replace_in_file(self, os.path.join(self.source_folder, "implot.cpp"),
                            "ImGuiButtonFlags_AllowItemOverlap",
                            "ImGuiButtonFlags_AllowOverlap")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="implot*.cpp", dst=os.path.join(self.package_folder, "res", "src"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["implot"]
