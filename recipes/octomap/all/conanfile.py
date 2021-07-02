from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.33.0"


class OctomapConan(ConanFile):
    name = "octomap"
    description = "An Efficient Probabilistic 3D Mapping Framework Based on Octrees."
    license = "BSD-3-Clause"
    topics = ("conan", "octomap", "octree", "3d", "robotics")
    homepage = "https://github.com/OctoMap/octomap"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "openmp": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "openmp": False
    }

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.shared and self.settings.compiler.get_safe("runtime") == "MTd":
            raise ConanInvalidConfiguration("shared octomap doesn't support MTd runtime")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["OCTOMAP_OMP"] = self.options.openmp
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        tools.replace_in_file(os.path.join(self._source_subfolder, "octomap", "CMakeLists.txt"),
                              "SET( BASE_DIR ${CMAKE_SOURCE_DIR} )",
                              "SET( BASE_DIR ${CMAKE_BINARY_DIR} )")
        compiler_settings = os.path.join(self._source_subfolder, "octomap", "CMakeModules", "CompilerSettings.cmake")
        # Do not force PIC
        tools.replace_in_file(compiler_settings, "ADD_DEFINITIONS(-fPIC)", "")
        # No -Werror
        if tools.Version(self.version) >= "1.9.6":
            tools.replace_in_file(compiler_settings, "-Werror", "")

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=os.path.join(self._source_subfolder, "octomap"))
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {
                self._octomath_target: "octomap::{}".format(self._octomath_target),
                self._octomap_target: "octomap::{}".format(self._octomap_target),
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
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

    @property
    def _octomath_target(self):
        return "octomath" if self.options.shared else "octomath-static"

    @property
    def _octomap_target(self):
        return "octomap" if self.options.shared else "octomap-static"

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "octomap"
        self.cpp_info.names["cmake_find_package_multi"] = "octomap"
        self.cpp_info.names["pkg_config"] = "octomap"

        # octomath
        self.cpp_info.components["octomath"].names["cmake_find_package"] = self._octomath_target
        self.cpp_info.components["octomath"].names["cmake_find_package_multi"] = self._octomath_target
        self.cpp_info.components["octomath"].builddirs.append(self._module_subfolder)
        self.cpp_info.components["octomath"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["octomath"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["octomath"].libs = ["octomath"]
        if self.settings.os == "Linux":
            self.cpp_info.components["octomath"].system_libs.append("m")
        # octomap
        self.cpp_info.components["octomaplib"].names["cmake_find_package"] = self._octomap_target
        self.cpp_info.components["octomaplib"].names["cmake_find_package_multi"] = self._octomap_target
        self.cpp_info.components["octomaplib"].builddirs.append(self._module_subfolder)
        self.cpp_info.components["octomaplib"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["octomaplib"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["octomaplib"].libs = ["octomap"]
        self.cpp_info.components["octomaplib"].requires = ["octomath"]
