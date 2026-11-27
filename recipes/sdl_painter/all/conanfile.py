from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.scm import Version
import os


required_conan_version = ">=2.0.9"


class SdlPainterConan(ConanFile):
    name = "sdl_painter"
    description = ("Modern C++17 2D drawing library for SDL3 with "
                   "interchangeable OpenGL 3.3 and Vulkan 1.1 backends.")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/yazilimperver/sdl-painter"
    topics = ("sdl3", "2d-graphics", "drawing-library", "opengl", "vulkan", "rendering")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_vulkan": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_vulkan": False,
    }
    implements = ["auto_shared_fpic"]

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {"gcc": "8", "clang": "7", "apple-clang": "12", "msvc": "192"}

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # SDL3 and glm types appear in the public headers.
        self.requires("sdl/3.4.16", transitive_headers=True, transitive_libs=True)
        self.requires("glm/1.0.3", transitive_headers=True)
        self.requires("sdl_ttf/3.2.2")
        self.requires("glad/0.1.36")
        self.requires("stb/cci.20240531")
        self.requires("spdlog/1.17.0")
        self.requires("opengl/system")
        if self.options.with_vulkan:
            self.requires("vulkan-loader/1.4.357.0")
            self.requires("vulkan-headers/1.4.357.0")

    def validate(self):
        # Only the OpenGL and Vulkan backends exist upstream; macOS is not supported yet.
        if self.settings.os not in ("Linux", "Windows", "FreeBSD"):
            raise ConanInvalidConfiguration(f"{self.ref} does not support {self.settings.os} yet.")
        check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.21 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SDLPAINTER_WITH_VULKAN"] = bool(self.options.with_vulkan)
        tc.cache_variables["SDLPAINTER_BUILD_EXAMPLES"] = False
        tc.cache_variables["SDLPAINTER_BUILD_TESTS"] = False
        tc.cache_variables["SDLPAINTER_WARNINGS_AS_ERRORS"] = False
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
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "sdl_painter")

        core = self.cpp_info.components["core"]
        core.set_property("cmake_target_name", "sdl_painter::sdl_painter")
        core.libs = ["sdl_painter"]
        core.requires = ["sdl::sdl", "glm::glm", "sdl_ttf::sdl_ttf", "glad::glad",
                         "stb::stb", "spdlog::spdlog", "opengl::opengl"]
        if not self.options.shared:
            core.defines.append("SDLPAINTER_STATIC_DEFINE")
        if self.options.with_vulkan:
            core.requires.extend(["vulkan-loader::vulkan-loader",
                                  "vulkan-headers::vulkan-headers"])
            core.defines.append("SDLPAINTER_HAS_VULKAN")
        if self.settings.os in ("Linux", "FreeBSD"):
            core.system_libs.extend(["m", "pthread", "dl"])

        # Optional window/event-loop layer on top of the drawing library.
        app = self.cpp_info.components["app"]
        app.set_property("cmake_target_name", "sdl_painter::app")
        app.libs = ["sdl_painter_app"]
        app.requires = ["core", "spdlog::spdlog"]
        if not self.options.shared:
            app.defines.append("SDLPAINTER_APP_STATIC_DEFINE")
