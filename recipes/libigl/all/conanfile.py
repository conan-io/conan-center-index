import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir, replace_in_file, export_conandata_patches, apply_conandata_patches
from conan.tools.microsoft import is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class LibiglConan(ConanFile):
    name = "libigl"
    description = "Simple C++ geometry processing library"
    # As per https://libigl.github.io/license/, the library itself is MPL-2, components are not
    # No issue as we don't build them, but if done so in the future, please update this field!
    license = "MPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libigl.github.io/"
    topics = ("geometry", "matrices", "algorithms", "header-only")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "header_only": [True, False],
    }
    default_options = {
        "fPIC": True,
        "header_only": False,
    }

    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "6",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.header_only:
            self.options.rm_safe("fPIC")
            # No automatic detection for non "library" package-types, manually override
            self.package_type = "header-library"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) >= "2.5.0":
            self.requires("eigen/3.4.0", transitive_headers=True)
        else:
            # 3.4.0 is not compatible with older versions
            self.requires("eigen/3.3.9", transitive_headers=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()

    def validate(self):
        if "arm" in self.settings.arch or self.settings.arch == "x86":
            raise ConanInvalidConfiguration(f"Not available for arm. Requested arch: {self.settings.arch}")
        if is_msvc_static_runtime(self) and not self.options.header_only:
            raise ConanInvalidConfiguration("Visual Studio build with MT runtime is not supported")

        def loose_lt_semver(v1, v2):
            return all(int(p1) < int(p2) for p1, p2 in zip(str(v1).split("."), str(v2).split(".")))

        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if min_version and loose_lt_semver(self.settings.compiler.version, min_version):
            raise ConanInvalidConfiguration(
                f"{self.name} requires C++{self._minimum_cpp_standard} support. The current compiler"
                f" {self.settings.compiler} {self.settings.compiler.version} does not support it."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = CMakeToolchain(self)
        tc.cache_variables["LIBIGL_INSTALL"] = True
        tc.cache_variables["LIBIGL_EXPORT_TARGETS"] = True
        tc.cache_variables["LIBIGL_USE_STATIC_LIBRARY"] = not self.options.header_only
        tc.cache_variables["LIBIGL_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0048"] = "NEW"

        # All these dependencies are needed to build the examples or the tests
        tc.cache_variables["LIBIGL_BUILD_TUTORIALS"] = False
        tc.cache_variables["LIBIGL_BUILD_TESTS"] = False
        tc.cache_variables["LIBIGL_BUILD_PYTHON"] = False

        tc.cache_variables["LIBIGL_WITH_CGAL"] = False
        tc.cache_variables["LIBIGL_WITH_COMISO"] = False
        tc.cache_variables["LIBIGL_WITH_CORK"] = False
        tc.cache_variables["LIBIGL_WITH_EMBREE"] = False
        tc.cache_variables["LIBIGL_WITH_MATLAB"] = False
        tc.cache_variables["LIBIGL_WITH_MOSEK"] = False
        tc.cache_variables["LIBIGL_WITH_OPENGL"] = False
        tc.cache_variables["LIBIGL_WITH_OPENGL_GLFW"] = False
        tc.cache_variables["LIBIGL_WITH_OPENGL_GLFW_IMGUI"] = False
        tc.cache_variables["LIBIGL_WITH_PNG"] = False
        tc.cache_variables["LIBIGL_WITH_TETGEN"] = False
        tc.cache_variables["LIBIGL_WITH_TRIANGLE"] = False
        tc.cache_variables["LIBIGL_WITH_XML"] = False
        tc.cache_variables["LIBIGL_WITH_PYTHON"] = False
        tc.cache_variables["LIBIGL_WITH_PREDICATES"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if Version(self.version) < "2.4.0":
            libigl_cmake = os.path.join(self.source_folder, "cmake", "libigl.cmake")
            replace_in_file(self, libigl_cmake, "-fPIC", "")
            replace_in_file(self, libigl_cmake, "INTERFACE_POSITION_INDEPENDENT_CODE ON", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.source_path.parent)
        try:
            cmake.build()
        except Exception:
            # Workaround for C3I running out of memory during build
            cmake.build(cli_args=["-j1"])

    def package(self):
        cmake = CMake(self)
        cmake.install()
        # If components are built and packaged in the future, uncomment this line, their license is different
        # copy(self, "LICENSE.GPL", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "LICENSE.MPL2", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        if not self.options.header_only:
            rm(self, "*.c", self.package_folder, recursive=True)
            rm(self, "*.cpp", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libigl")
        self.cpp_info.set_property("cmake_target_name", "igl::igl")

        self.cpp_info.components["common"].set_property("cmake_target_name", "igl::common")
        self.cpp_info.components["common"].requires = ["eigen::eigen"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["common"].system_libs = ["pthread"]

        self.cpp_info.components["core"].set_property("cmake_target_name", "igl::core")
        self.cpp_info.components["core"].requires = ["common"]
        if not self.options.header_only:
            self.cpp_info.components["core"].libs = ["igl"]
            self.cpp_info.components["core"].defines.append("IGL_STATIC_LIBRARY")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "libigl"
        self.cpp_info.filenames["cmake_find_package_multi"] = "libigl"
        self.cpp_info.names["cmake_find_package"] = "igl"
        self.cpp_info.names["cmake_find_package_multi"] = "igl"
