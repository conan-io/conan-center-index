from conans import ConanFile, CMake, tools
import os
import textwrap

required_conan_version = ">=1.43.0"


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

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if self.settings.os == "Windows":
            self._cmake.definitions["OPENMESH_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["BUILD_APPS"] = False
        self._cmake.definitions["OPENMESH_DOCS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "libdata"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        if self.settings.os != "Windows":
            tools.remove_files_by_mask(
                os.path.join(self.package_folder, "lib"),
                "*.a" if self.options.shared else "*.[so|dylib]*",
            )
        # TODO: to remove in conan v2 once cmake_find_package* removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {
                "OpenMeshCore": "OpenMesh::OpenMeshCore",
                "OpenMeshTools": "OpenMesh::OpenMeshTools",
            }
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

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
        if self._is_msvc:
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
