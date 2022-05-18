import glob
import os

from conans import CMake, ConanFile, tools
import conan.tools.files
import textwrap


class IgnitionCmakeConan(ConanFile):
    name = "ignition-cmake"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gazebosim/gz-cmake"
    description = "A set of CMake modules that are used by the C++-based Ignition projects."
    topics = ("ignition", "robotics", "cmake")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"
    exports_sources = "CMakeLists.txt", "patches/**"

    _cmake = None

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def _configure_cmake(self):
        if self._cmake is not None:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CMAKE_INSTALL_DATAROOTDIR"] = "lib"
        self._cmake.definitions["SKIP_component_name"] = False
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        version_major = self.version.split(".")[0]
        conan.tools.files.rename(
             self, f"gz-cmake-ignition-cmake{version_major}_{self.version}",
             self._source_subfolder
            )



    def build(self):
        version_major = tools.Version(self.version).major
        ignition_cmake_dir = os.path.join(self.package_folder, "lib", "cmake", f"ignition-cmake{version_major}", "cmake2")
        os. environ['IGNITION_CMAKE_DIR'] = f"{ignition_cmake_dir}"
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        version_major = tools.Version(self.version).major
        cmake_config_files_dir = os.path.join(self.package_folder, "lib", "cmake",f"ignition-cmake{version_major}")
        files = os.listdir(cmake_config_files_dir)

        # retain the special config file for utilities target provided by ignition-cmake
        # removing it from the list
        files.remove(f"ignition-cmake{version_major}-utilities-targets.cmake")

        # remvoe all other xxx.cmake files from the list
        for file in files:
            if file.endswith(".cmake"):
                os.remove(os.path.join(cmake_config_files_dir, file))
        
        # add version information for downstream dependencies consuming ign-cmake through cmake_find_package generators 
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path),
            tools.Version(self.version)
        )

    @staticmethod
    def _create_cmake_module_variables(module_file, version):
        # the version info is needed by downstream ignition-dependencies
        content = textwrap.dedent("""\
            set(ignition-cmake{major}_VERSION_MAJOR {major})
            set(ignition-cmake{major}_VERSION_MINOR {minor})
            set(ignition-cmake{major}_VERSION_PATCH {patch})
            set(ignition-cmake{major}_VERSION_STRING "{major}.{minor}.{patch}")
        """.format(major=version.major, minor=version.minor, patch=version.patch))
        tools.save(module_file, content)

    def package_info(self):
        version_major = tools.Version(self.version).major
        ign_cmake_component = f"ignition-cmake{version_major}"
        base_module_path = os.path.join(self.package_folder, "lib", "cmake", ign_cmake_component)

        self.cpp_info.names["cmake_find_package"] = ign_cmake_component
        self.cpp_info.names["cmake_find_package_multi"] = ign_cmake_component
        self.cpp_info.names["cmake_paths"] = ign_cmake_component

        self.cpp_info.components[ign_cmake_component].names["cmake_find_package"] = ign_cmake_component
        self.cpp_info.components[ign_cmake_component].names["cmake_find_package_multi"] = ign_cmake_component
        self.cpp_info.components[ign_cmake_component].names["cmake_paths"] = ign_cmake_component
        self.cpp_info.components[ign_cmake_component].builddirs.append(os.path.join(base_module_path, f"cmake{version_major}"))
        self.cpp_info.components[ign_cmake_component].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components[ign_cmake_component].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components[ign_cmake_component].build_modules["cmake_paths"] = [self._module_file_rel_path]

        self.cpp_info.components["utilities"].names["cmake_find_package"] = "utilities"
        self.cpp_info.components["utilities"].names["cmake_find_package_multi"] = "utilities"
        self.cpp_info.components["utilities"].names["cmake_paths"] = "utilities"
        self.cpp_info.components["utilities"].includedirs.append(f"include/ignition/cmake{version_major}")
        
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path])
        self.cpp_info.components["utilities"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["utilities"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["utilities"].build_modules["cmake_paths"] = [self._module_file_rel_path]
        
        ## cpp_info for the ignition-cmake-utilities-targets.cmake file
        utils_targets_file_path = os.path.join(base_module_path, f"{ign_cmake_component}-utilities-targets.cmake")
        self.cpp_info.components["utilities"].build_modules["cmake_find_package"].append(utils_targets_file_path)
        self.cpp_info.components["utilities"].build_modules["cmake_find_package_multi"].append(utils_targets_file_path)
        self.cpp_info.components["utilities"].build_modules["cmake_paths"].append(utils_targets_file_path)
