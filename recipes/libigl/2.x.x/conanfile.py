import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.files import get, rm, rmdir, apply_conandata_patches, export_conandata_patches
from conan.tools.scm import Version
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.microsoft import is_msvc_static_runtime
from conan.errors import ConanInvalidConfiguration


required_conan_version = ">=1.52.0"


class LibiglConan(ConanFile):
    name = "libigl"
    description = "Simple C++ geometry processing library"
    topics = ("geometry", "matrices", "algorithms")
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["patches/**"]
    homepage = "https://libigl.github.io/"
    license = "MPL-2.0"
    settings = "os", "arch", "compiler", "build_type"
    options = {"header_only": [True, False], "fPIC": [True, False]}
    default_options = {"header_only": True, "fPIC": True}

    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "1920",
            "gcc": "6",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.header_only:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def layout(self):
        if not self.options.header_only:
            cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/3.4.0")
        if Version(self.version) >= "2.4.0":
            self.requires("gmp/6.2.1")
            self.requires("mpfr/4.1.0")

    def validate(self):
        if self.info.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        minimum_version = self._minimum_compilers_version.get(str(self.info.settings.compiler), False)
        if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._minimum_cpp_standard}, which your compiler does not support.")
        if self.info.options.get_safe("header_only") is None and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration(f"{self.ref} is not supported by {self.info.settings.compiler} with MT runtime")
        if cross_building(self) and Version(self.version) < "2.4.0" and not is_apple_os(self):
            raise ConanInvalidConfiguration(f"{self.ref} can not be cross-compiled.")

    def build_requirements(self):
        self.tool_requires("cmake/3.24.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self.source_folder)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIBIGL_USE_STATIC_LIBRARY"] = not self.options.header_only
        tc.variables["LIBIGL_BUILD_TUTORIALS"] = False
        tc.variables["LIBIGL_BUILD_TESTS"] = False
        tc.cache_variables["CMAKE_BUILD_PARALLEL_LEVEL"] = 1
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0091"] = "NEW"
        tc.cache_variables["CMAKE_VERBOSE_MAKEFILE"] = True

        if Version(self.version) < "2.4.0":
            tc.variables["LIBIGL_EXPORT_TARGETS"] = True
            tc.variables["LIBIGL_BUILD_PYTHON"] = False
            tc.variables["LIBIGL_WITH_CGAL"] = False
            tc.variables["LIBIGL_WITH_COMISO"] = False
            tc.variables["LIBIGL_WITH_CORK"] = False
            tc.variables["LIBIGL_WITH_EMBREE"] = False
            tc.variables["LIBIGL_WITH_MATLAB"] = False
            tc.variables["LIBIGL_WITH_MOSEK"] = False
            tc.variables["LIBIGL_WITH_OPENGL"] = False
            tc.variables["LIBIGL_WITH_OPENGL_GLFW"] = False
            tc.variables["LIBIGL_WITH_OPENGL_GLFW_IMGUI"] = False
            tc.variables["LIBIGL_WITH_PNG"] = False
            tc.variables["LIBIGL_WITH_XML"] = False
            tc.variables["LIBIGL_WITH_TETGEN"] = False
            tc.variables["LIBIGL_WITH_TRIANGLE"] = False
            tc.variables["LIBIGL_WITH_PYTHON"] = False
            tc.variables["LIBIGL_WITH_PREDICATES"] = False
        else:
            tc.variables["LIBIGL_INSTALL"] = True
            tc.variables["LIBIGL_COPYLEFT_CGAL"] = False
            tc.variables["LIBIGL_COPYLEFT_COMISO"] = False
            tc.variables["LIBIGL_EMBREE"] = False
            tc.variables["LIBIGL_RESTRICTED_MATLAB"] = False
            tc.variables["LIBIGL_RESTRICTED_MOSEK"] = False
            tc.variables["LIBIGL_OPENGL"] = False
            tc.variables["LIBIGL_GLFW"] = False
            tc.variables["LIBIGL_IMGUI"] = False
            tc.variables["LIBIGL_PNG"] = False
            tc.variables["LIBIGL_XML"] = False
            tc.variables["LIBIGL_COPYLEFT_TETGEN"] = False
            tc.variables["LIBIGL_RESTRICTED_TRIANGLE"] = False
            tc.variables["LIBIGL_PREDICATES"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        self.copy("LICENSE.GPL", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        self.copy("LICENSE.MPL2", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        if not self.options.header_only:
            rm(self, "*.c", self.package_folder, recursive=True)
            rm(self, "*.cpp", self.package_folder, recursive=True)

    def package_id(self):
        if self.options.header_only:
            self.info.clear()

    def package_info(self):
        # TODO: Remove after Conan 2.0
        self.cpp_info.filenames["cmake_find_package"] = "libigl"
        self.cpp_info.filenames["cmake_find_package_multi"] = "libigl"
        self.cpp_info.names["cmake_find_package"] = "igl"
        self.cpp_info.names["cmake_find_package_multi"] = "igl"
        self.cpp_info.set_property("cmake_file_name", "libigl")

        self.cpp_info.components["igl_common"].names["cmake_find_package"] = "common"
        self.cpp_info.components["igl_common"].names["cmake_find_package_multi"] = "common"
        self.cpp_info.components["igl_common"].set_property("cmake_target_name", "igl::common")
        self.cpp_info.components["igl_common"].libs = []
        self.cpp_info.components["igl_common"].requires = ["eigen::eigen"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["igl_common"].system_libs = ["pthread"]

        self.cpp_info.components["igl_core"].names["cmake_find_package"] = "core"
        self.cpp_info.components["igl_core"].names["cmake_find_package_multi"] = "core"
        self.cpp_info.components["igl_core"].set_property("cmake_target_name", "igl::core")
        self.cpp_info.components["igl_core"].requires = ["igl_common"]
        if not self.options.header_only:
            self.cpp_info.components["igl_core"].libs = ["igl"]
            self.cpp_info.components["igl_core"].defines.append("IGL_STATIC_LIBRARY")
