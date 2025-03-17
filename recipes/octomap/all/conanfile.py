from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
from conan.tools.build import check_min_cppstd
import os
import textwrap

required_conan_version = ">=1.53.0"

class OctomapConan(ConanFile):
    name = "octomap"
    description = "An Efficient Probabilistic 3D Mapping Framework Based on Octrees."
    license = "BSD-3-Clause"
    topics = ("octree", "3d", "robotics")
    homepage = "https://github.com/OctoMap/octomap"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "openmp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "openmp": False,
    }

    @property
    def _min_cppstd(self):
        return 11

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("shared octomap doesn't support MT runtime")

        if Version(self.version) >= "1.10.0" and self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["OCTOMAP_OMP"] = self.options.openmp
        tc.variables["BUILD_TESTING"] = False
        if is_msvc(self) and self.options.shared:
            tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        if Version(self.version) >= "1.10.0":
            tc.variables["CMAKE_CXX_STANDARD"] = self.settings.compiler.get_safe("cppstd", "11").replace("gnu", "")
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Create binaries in build tree instead of source tree
        replace_in_file(self, os.path.join(self.source_folder, "octomap", "CMakeLists.txt"),
                              "SET( BASE_DIR ${CMAKE_SOURCE_DIR} )",
                              "SET( BASE_DIR ${CMAKE_BINARY_DIR} )")
        compiler_settings = os.path.join(self.source_folder, "octomap", "CMakeModules", "CompilerSettings.cmake")
        # Do not force PIC
        replace_in_file(self, compiler_settings, "ADD_DEFINITIONS(-fPIC)", "")
        # No -Werror
        if Version(self.version) >= "1.9.6":
            replace_in_file(self, compiler_settings, "-Werror", "")
        # we want a clean rpath in installed shared libs
        replace_in_file(self, compiler_settings, "set(CMAKE_INSTALL_RPATH \"${CMAKE_INSTALL_PREFIX}/lib\")", "")
        replace_in_file(self, compiler_settings, "set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "octomap"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=os.path.join(self.source_folder, "octomap"),
                                  dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        # TODO: to remove in conan v2 once cmake_find_package_* generators are removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {
                self._octomath_target: f"octomap::{self._octomath_target}",
                self._octomap_target: f"octomap::{self._octomap_target}",
            }
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    @property
    def _octomath_target(self):
        return "octomath" if self.options.shared else "octomath-static"

    @property
    def _octomap_target(self):
        return "octomap" if self.options.shared else "octomap-static"

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "octomap")
        self.cpp_info.set_property("pkg_config_name", "octomap")

        # octomath
        self.cpp_info.components["octomath"].set_property("cmake_target_name", self._octomath_target)
        self.cpp_info.components["octomath"].libs = ["octomath"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["octomath"].system_libs.append("m")
        # octomap
        self.cpp_info.components["octomaplib"].set_property("cmake_target_name", self._octomap_target)
        self.cpp_info.components["octomaplib"].libs = ["octomap"]
        self.cpp_info.components["octomaplib"].requires = ["octomath"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators are removed
        self.cpp_info.components["octomath"].names["cmake_find_package"] = self._octomath_target
        self.cpp_info.components["octomath"].names["cmake_find_package_multi"] = self._octomath_target
        self.cpp_info.components["octomath"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["octomath"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["octomaplib"].names["cmake_find_package"] = self._octomap_target
        self.cpp_info.components["octomaplib"].names["cmake_find_package_multi"] = self._octomap_target
        self.cpp_info.components["octomaplib"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["octomaplib"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
