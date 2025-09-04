from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os


required_conan_version = ">=2.0.9"

class PackageConan(ConanFile):
    name = "sgltk"
    description = "A collection of easy to use OpenGL tools."
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/pyth/sgltk"
    topics = ("c-plus-plus", "opengl", "sdl2")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_sdl_ttf": [True, False],
        "with_assimp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
		"with_sdl_ttf": True,
		"with_assimp": True,
    }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("glm/1.0.1")
        self.requires("glew/2.2.0")
        self.requires("sdl/2.28.3")
        self.requires("sdl_image/2.8.2")
        if self.options.with_sdl_ttf:
            self.requires("sdl_ttf/2.24.0")
        if self.options.with_assimp:
            self.requires("assimp/5.4.3")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["PACKAGE_BUILD_TESTS"] = False
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

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "sgltk")
        self.cpp_info.set_property("cmake_target_name", "sgltk::sgltk")

        self.cpp_info.libs = ["sgltk" if self.options.shared else "sgltk_static"]

        reqs = [
            "glm::glm",
            "glew::glew",
            "sdl::sdl",
            "sdl_image::sdl_image",
        ]
        if self.options.with_sdl_ttf:
            reqs.append("sdl_ttf::sdl_ttf")
        if self.options.with_assimp:
            reqs.append("assimp::assimp")

        self.cpp_info.requires = reqs
