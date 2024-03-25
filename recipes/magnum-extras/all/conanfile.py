import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir, save

required_conan_version = ">=1.53.0"


class MagnumExtrasConan(ConanFile):
    name = "magnum-extras"
    description = "Extras for the Magnum C++11/C++14 graphics engine"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://magnum.graphics"
    topics = ("magnum", "graphics", "rendering", "3d", "2d", "opengl")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "player": [True, False],
        "ui": [True, False],
        "ui_gallery": [True, False],
        "application": ["android", "emscripten", "glfw", "glx", "sdl2", "xegl"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "player": True,
        "ui": True,
        "ui_gallery": True,
        "application": "sdl2",
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if self.settings.os == "Android":
            self.options.application = "android"
        if self.settings.os == "Emscripten":
            self.options.application = "emscripten"
            # FIXME: Requires 'magnum:basis_importer=True'
            self.options.player = False
            # FIXME: Fails to compile
            self.options.ui_gallery = False

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # https://github.com/mosra/magnum-extras/blob/v2020.06/src/Magnum/Ui/Anchor.h#L32-L33
        self.requires(f"magnum/{self.version}", transitive_headers=True, transitive_libs=True)
        self.requires(f"corrade/{self.version}", transitive_headers=True, transitive_libs=True)
        if self.settings.os in ["iOS", "Emscripten", "Android"] and self.options.ui_gallery:
            self.requires(f"magnum-plugins/{self.version}")

    def validate(self):
        opt_name = f"{self.options.application}_application"
        if not self.dependencies["magnum"].options.get_safe(opt_name):
            raise ConanInvalidConfiguration(f"Magnum needs option '{opt_name}=True'")
        if self.settings.os == "Emscripten" and self.dependencies["magnum"].options.target_gl == "gles2":
            raise ConanInvalidConfiguration("OpenGL ES 3 required, use option 'magnum:target_gl=gles3'")

    def build_requirements(self):
        self.tool_requires(f"corrade/{self.version}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_STATIC"] = not self.options.shared
        tc.variables["BUILD_STATIC_PIC"] = self.options.get_safe("fPIC", False)
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_GL_TESTS"] = False
        tc.variables["WITH_PLAYER"] = self.options.player
        tc.variables["WITH_UI"] = self.options.ui
        tc.variables["WITH_UI_GALLERY"] = self.options.ui_gallery
        tc.variables["MAGNUM_INCLUDE_INSTALL_DIR"] = os.path.join("include", "Magnum")
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        'set(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/modules/" ${CMAKE_MODULE_PATH})',
                        "")

        # Remove unnecessary dependency on UseEmscripten
        # https://github.com/mosra/magnum/issues/490
        save(self, os.path.join(self.source_folder, "UseEmscripten.cmake"), "")

        app_name = "{}Application".format(
            "XEgl" if self.options.application == "xegl" else str(self.options.application).capitalize()
        )
        for cmakelist in [
            os.path.join("src", "Magnum", "Ui", "CMakeLists.txt"),
            os.path.join("src", "player", "CMakeLists.txt"),
        ]:
            replace_in_file(self, os.path.join(self.source_folder, cmakelist),
                            "Magnum::Application", f"Magnum::{app_name}")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "MagnumExtras")
        self.cpp_info.names["cmake_find_package"] = "MagnumExtras"
        self.cpp_info.names["cmake_find_package_multi"] = "MagnumExtras"

        lib_suffix = "-d" if self.settings.build_type == "Debug" else ""
        if self.options.ui:
            self.cpp_info.components["ui"].set_property("cmake_target_name", "MagnumExtras::Ui")
            self.cpp_info.components["ui"].names["cmake_find_package"] = "Ui"
            self.cpp_info.components["ui"].names["cmake_find_package_multi"] = "Ui"
            self.cpp_info.components["ui"].libs = [f"MagnumUi{lib_suffix}"]
            self.cpp_info.components["ui"].requires = [
                "corrade::interconnect",
                "magnum::magnum_main",
                "magnum::gl",
                "magnum::text",
            ]

        if self.options.player or self.options.ui_gallery:
            bin_path = os.path.join(self.package_folder, "bin")
            self.env_info.path.append(bin_path)
