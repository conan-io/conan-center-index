from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rm, rmdir, save
from conan.tools.microsoft import is_msvc
import os
import textwrap

required_conan_version = ">=1.50.0"


class OpenmeshConan(ConanFile):
    name = "openmesh"
    description = "OpenMesh is a generic and efficient data structure for " \
                  "representing and manipulating polygonal meshes."
    license = "BSD-3-Clause"
    topics = ("openmesh", "mesh", "structure", "geometry")
    homepage = "https://www.graphics.rwth-aachen.de/software/openmesh"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
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
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.settings.os == "Windows":
            tc.variables["OPENMESH_BUILD_SHARED"] = self.options.shared
        tc.variables["BUILD_APPS"] = False
        tc.variables["OPENMESH_DOCS"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "libdata"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        if self.settings.os != "Windows":
            rm(self, "*.a" if self.options.shared else "*.[so|dylib]*", os.path.join(self.package_folder, "lib"))

        # TODO: to remove in conan v2 once cmake_find_package* removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {
                "OpenMeshCore": "OpenMesh::OpenMeshCore",
                "OpenMeshTools": "OpenMesh::OpenMeshTools",
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

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenMesh")
        self.cpp_info.set_property("pkg_config_name", "openmesh")

        suffix = "d" if self.settings.build_type == "Debug" else ""
        # OpenMeshCore
        self.cpp_info.components["openmeshcore"].set_property("cmake_target_name", "OpenMeshCore")
        self.cpp_info.components["openmeshcore"].libs = ["OpenMeshCore" + suffix]
        if not self.options.shared:
            self.cpp_info.components["openmeshcore"].defines.append("OM_STATIC_BUILD")
        if is_msvc(self):
            self.cpp_info.components["openmeshcore"].defines.append("_USE_MATH_DEFINES")

        # OpenMeshTools
        self.cpp_info.components["openmeshtools"].set_property("cmake_target_name", "OpenMeshTools")
        self.cpp_info.components["openmeshtools"].libs = ["OpenMeshTools" + suffix]
        self.cpp_info.components["openmeshtools"].requires = ["openmeshcore"]

        # TODO: to remove in conan v2 once cmake_find_package* removed
        self.cpp_info.names["cmake_find_package"] = "OpenMesh"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenMesh"
        self.cpp_info.components["openmeshcore"].names["cmake_find_package"] = "OpenMeshCore"
        self.cpp_info.components["openmeshcore"].names["cmake_find_package_multi"] = "OpenMeshCore"
        self.cpp_info.components["openmeshcore"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["openmeshcore"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["openmeshtools"].names["cmake_find_package"] = "OpenMeshTools"
        self.cpp_info.components["openmeshtools"].names["cmake_find_package_multi"] = "OpenMeshTools"
        self.cpp_info.components["openmeshtools"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["openmeshtools"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
