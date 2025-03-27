from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir, apply_conandata_patches, export_conandata_patches
import os

required_conan_version = ">=2.0.9"


class ImGuiSFMLConan(ConanFile):
    name = "imgui-sfml"
    description = "ImGui-SFML integrates Dear ImGui with SFML, enabling easy creation of GUIs for SFML applications."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/SFML/imgui-sfml"
    topics = ("gui", "graphical", "sfml", "imgui")
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
        self.requires("sfml/2.6.2", transitive_headers=True)
        self.requires("imgui/1.91.8", transitive_headers=True, transitive_libs=True)
        self.requires("opengl/system")

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["IMGUI_SFML_FIND_SFML"] = True
        tc.cache_variables["IMGUI_DIR"] = "UNUSED"
        tc.cache_variables["IMGUI_SFML_IMGUI_DEMO"] = False

        tc.cache_variables["IMGUI_SFML_BUILD_TESTING"] = False
        tc.cache_variables["IMGUI_SFML_BUILD_EXAMPLES"] = False
        tc.generate()

        tc = CMakeDeps(self)
        tc.set_property("imgui", "cmake_file_name", "ImGui")
        tc.set_property("imgui", "cmake_additional_variables_prefixes", ["IMGUI"])
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        postfix = ""
        if self.options.shared and self.settings.build_type == "Debug":
            postfix = "_d"
        self.cpp_info.libs = ["ImGui-SFML" + postfix]

        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["imm32"]

        self.cpp_info.set_property("cmake_file_name", "ImGui-SFML")
        self.cpp_info.set_property("cmake_target_name", "ImGui-SFML::ImGui-SFML")
