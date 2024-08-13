from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rm, rmdir, mkdir
import os


required_conan_version = ">=1.53.0"


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

    @property
    def _min_cppstd(self):
        return 11

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("sfml/2.6.1", transitive_headers=True)
        self.requires("imgui/1.91.0")
        self.requires("opengl/system")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["IMGUI_DIR"] = self.dependencies["imgui"].package_folder
        tc.variables["IMGUI_INCLUDE_DIR"] = self.dependencies["imgui"].cpp_info.includedir
        tc.generate()

        tc = CMakeDeps(self)
        tc.set_property("imgui", "cmake_file_name", "ImGui")
        tc.generate()

    def _patch_sources(self):
        # This is a workaround to avoid installing vendorized imgui headers as well to the package folder
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), 'list(APPEND IMGUI_SFML_PUBLIC_HEADERS "${IMGUI_PUBLIC_HEADERS}")', "")

    def build(self):
        self._patch_sources()
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
        self.cpp_info.libs = ["ImGui-SFML"]

        self.cpp_info.set_property("cmake_file_name", "ImGui-SFML")
        self.cpp_info.set_property("cmake_target_name", "ImGui-SFML::ImGui-SFML")
