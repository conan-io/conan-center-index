from conans import ConanFile, CMake, tools
import os
import textwrap

required_conan_version = ">=1.33.0"


class TinyObjLoaderConan(ConanFile):
    name = "tinyobjloader"
    description = "Tiny but powerful single file wavefront obj loader"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/syoyo/tinyobjloader"
    topics = ("conan", "tinyobjloader", "wavefront", "geometry")

    settings = "os", "arch", "build_type", "compiler"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "double": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "double": False,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = self.name + "-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["TINYOBJLOADER_USE_DOUBLE"] = self.options.double
        self._cmake.definitions["TINYOBJLOADER_BUILD_TEST_LOADER"] = False
        self._cmake.definitions["TINYOBJLOADER_COMPILATION_SHARED"] = self.options.shared
        self._cmake.definitions["TINYOBJLOADER_BUILD_OBJ_STICHER"] = False
        self._cmake.definitions["CMAKE_INSTALL_DOCDIR"] = "licenses"
        self._cmake.configure(build_dir=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "tinyobjloader"))
        cmake_target = "tinyobjloader_double" if self.options.double else "tinyobjloader"
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {cmake_target: "tinyobjloader::tinyobjloader"}
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

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "tinyobjloader"
        self.cpp_info.names["cmake_find_package_multi"] = "tinyobjloader"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        suffix = "_double" if self.options.double else ""
        self.cpp_info.names["pkg_config"] = "tinyobjloader" + suffix
        self.cpp_info.libs = ["tinyobjloader" + suffix]
        if self.options.double:
            self.cpp_info.defines.append("TINYOBJLOADER_USE_DOUBLE")
