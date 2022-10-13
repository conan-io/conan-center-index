from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.47.0"


class OctomapConan(ConanFile):
    name = "octomap"
    description = "An Efficient Probabilistic 3D Mapping Framework Based on Octrees."
    license = "BSD-3-Clause"
    topics = ("octomap", "octree", "3d", "robotics")
    homepage = "https://github.com/OctoMap/octomap"
    url = "https://github.com/conan-io/conan-center-index"

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

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.info.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("shared octomap doesn't support MT runtime")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["OCTOMAP_OMP"] = self.options.openmp
        tc.variables["BUILD_TESTING"] = False
        if is_msvc(self) and self.options.shared:
            tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
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
                self._octomath_target: "octomap::{}".format(self._octomath_target),
                self._octomap_target: "octomap::{}".format(self._octomap_target),
            }
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

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
