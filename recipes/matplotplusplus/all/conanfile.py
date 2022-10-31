from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"


class MatplotPlusPlusConan(ConanFile):
    name = "matplotplusplus"
    description = "A C++ Graphics Library for Data Visualization"
    license = "MIT"
    topics = ("matplot", "chart", "data-visualization", "data-science", "plot", "graphics", "graph")
    homepage = "https://alandefreitas.github.io/matplotplusplus"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "high_resolution_world_map": [True, False],
        "documentation_images": [True, False],
        "with_opengl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "high_resolution_world_map": True,
        "documentation_images": False,
        "with_opengl": False,
    }

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15",
            "msvc": "191",
            "clang": "6",
            "apple-clang": "10",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cimg/3.0.2")
        self.requires("nodesoup/cci.20200905")
        # FIXME: add gnuplot, it's a mandatory runtime dependency of matplot component
        if self.options.with_opengl:
            self.requires("glad/0.1.36")
            self.requires("glfw/3.3.8")

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
        if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_INSTALLER"] = True
        tc.variables["BUILD_PACKAGE"] = False
        tc.variables["BUILD_WITH_PEDANTIC_WARNINGS"] = False
        tc.variables["BUILD_WITH_SANITIZERS"] = False
        tc.variables["BUILD_WITH_EXCEPTIONS"] = False
        tc.variables["BUILD_HIGH_RESOLUTION_WORLD_MAP"] = self.options.high_resolution_world_map
        tc.variables["BUILD_FOR_DOCUMENTATION_IMAGES"] = self.options.documentation_images
        tc.variables["BUILD_EXPERIMENTAL_OPENGL_BACKEND"] = self.options.with_opengl
        tc.variables["WITH_SYSTEM_CIMG"] = True
        tc.variables["WITH_SYSTEM_NODESOUP"] = True
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Matplot++")
        self.cpp_info.set_property(
            "cmake_target_name",
            "Matplot++::matplot_opengl" if self.options.with_opengl else "Matplot++::matplot",
        )

        self.cpp_info.components["matplot"].set_property("cmake_target_name", "Matplot++::matplot")
        self.cpp_info.components["matplot"].libs = ["matplot"]
        self.cpp_info.components["matplot"].requires = ["cimg::cimg", "nodesoup::nodesoup"]
        if not self.options.shared:
            if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "9":
                self.cpp_info.components["matplot"].system_libs.append("stdc++fs")

        if self.options.with_opengl:
            self.cpp_info.components["matplot_opengl"].set_property("cmake_target_name", "Matplot++::matplot_opengl")
            self.cpp_info.components["matplot_opengl"].libs = ["matplot_opengl"]
            self.cpp_info.components["matplot_opengl"].requires = ["matplot", "glad::glad", "glfw::glfw"]

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "Matplot++"
        self.cpp_info.names["cmake_find_package_multi"] = "Matplot++"
