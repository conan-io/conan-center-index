import os
import textwrap

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class IgnitionCmakeConan(ConanFile):
    name = "ignition-cmake"
    description = "A set of CMake modules that are used by the C++-based Ignition projects."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gazebosim/gz-cmake"
    topics = ("ignition", "robotics", "cmake", "gazebo", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_INSTALL_DATAROOTDIR"] = "lib"
        tc.variables["SKIP_component_name"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "bin"))

        version_major = Version(self.version).major
        cmake_config_files_dir = os.path.join(self.package_folder, "lib", "cmake", f"ignition-cmake{version_major}")
        for file in os.listdir(cmake_config_files_dir):
            if file.endswith(".cmake"):
                if file == f"ignition-cmake{version_major}-utilities-targets.cmake":
                    # retain the special config file for utilities target provided by ignition-cmake
                    continue
                os.remove(os.path.join(cmake_config_files_dir, file))

        # add version information for downstream dependencies consuming ign-cmake through CMake generators
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path),
            Version(self.version)
        )

    def _create_cmake_module_variables(self, module_file, version):
        # the version info is needed by downstream ignition-dependencies
        content = textwrap.dedent(f"""\
            set(ignition-cmake{version.major}_VERSION_MAJOR {version.major})
            set(ignition-cmake{version.major}_VERSION_MINOR {version.minor})
            set(ignition-cmake{version.major}_VERSION_PATCH {version.patch})
            set(ignition-cmake{version.major}_VERSION_STRING "{version.major}.{version.minor}.{version.patch}")
        """)
        save(self, module_file, content)


    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.frameworkdirs = []

        version_major = Version(self.version).major
        ign_cmake_component = f"ignition-cmake{version_major}"
        self.cpp_info.set_property("cmake_file_name", ign_cmake_component)

        base_module_path = os.path.join("lib", "cmake", ign_cmake_component)
        ign_cmake_file = os.path.join(base_module_path, f"cmake{version_major}", "IgnCMake.cmake")
        utils_targets_file = os.path.join(base_module_path, f"{ign_cmake_component}-utilities-targets.cmake")
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path, ign_cmake_file, utils_targets_file])

        self.cpp_info.components[ign_cmake_component].set_property("cmake_target_name", f"{ign_cmake_component}::{ign_cmake_component}")
        self.cpp_info.components[ign_cmake_component].builddirs.append(os.path.join(base_module_path, f"cmake{version_major}"))

        self.cpp_info.components["utilities"].set_property("cmake_target_name", f"{ign_cmake_component}::utilities")
        self.cpp_info.components["utilities"].builddirs.append(os.path.join(base_module_path, f"cmake{version_major}"))
        self.cpp_info.components["utilities"].includedirs.append(os.path.join("include", "ignition", f"cmake{version_major}"))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = ign_cmake_component
        self.cpp_info.names["cmake_find_package_multi"] = ign_cmake_component
        self.cpp_info.names["cmake_paths"] = ign_cmake_component
        self.cpp_info.components[ign_cmake_component].names["cmake_find_package"] = ign_cmake_component
        self.cpp_info.components[ign_cmake_component].names["cmake_find_package_multi"] = ign_cmake_component
        self.cpp_info.components[ign_cmake_component].names["cmake_paths"] = ign_cmake_component
        self.cpp_info.components[ign_cmake_component].build_modules["cmake_find_package"] = [self._module_file_rel_path, ign_cmake_file]
        self.cpp_info.components[ign_cmake_component].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path, ign_cmake_file]
        self.cpp_info.components[ign_cmake_component].build_modules["cmake_paths"] = [self._module_file_rel_path, ign_cmake_file]
        self.cpp_info.components["utilities"].names["cmake_find_package"] = "utilities"
        self.cpp_info.components["utilities"].names["cmake_find_package_multi"] = "utilities"
        self.cpp_info.components["utilities"].names["cmake_paths"] = "utilities"
        self.cpp_info.components["utilities"].build_modules["cmake_find_package"] = [self._module_file_rel_path, ign_cmake_file, utils_targets_file]
        self.cpp_info.components["utilities"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path, ign_cmake_file, utils_targets_file]
        self.cpp_info.components["utilities"].build_modules["cmake_paths"] = [self._module_file_rel_path, ign_cmake_file, utils_targets_file]
