from conan import ConanFile, tools
from conans import CMake
import os
import textwrap

required_conan_version = ">=1.43.0"


class LibgeotiffConan(ConanFile):
    name = "libgeotiff"
    description = "Libgeotiff is an open source library normally hosted on top " \
                  "of libtiff for reading, and writing GeoTIFF information tags."
    license = ["MIT", "BSD-3-Clause"]
    topics = ("libgeotiff", "geotiff", "tiff")
    homepage = "https://github.com/OSGeo/libgeotiff"
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

    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

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
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("libtiff/4.3.0")
        self.requires("proj/9.0.0")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITH_UTILITIES"] = False
        self._cmake.definitions["WITH_TOWGS84"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=os.path.join(self._source_subfolder, "libgeotiff"))
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "doc"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_vars_file)
        )
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_target_file),
            {"geotiff_library": "geotiff::geotiff"}
        )

    @staticmethod
    def _create_cmake_module_variables(module_file):
        content = textwrap.dedent("""\
            if(DEFINED GeoTIFF_FOUND)
                set(GEOTIFF_FOUND ${GeoTIFF_FOUND})
            endif()
            if(DEFINED GeoTIFF_INCLUDE_DIR)
                set(GEOTIFF_INCLUDE_DIR ${GeoTIFF_INCLUDE_DIR})
            endif()
            if(DEFINED GeoTIFF_LIBRARIES)
                set(GEOTIFF_LIBRARIES ${GeoTIFF_LIBRARIES})
            endif()
        """)
        tools.files.save(self, module_file, content)

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
        tools.files.save(self, module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_vars_file(self):
        return os.path.join("lib", "cmake", "conan-official-{}-variables.cmake".format(self.name))

    @property
    def _module_target_file(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "GeoTIFF")
        self.cpp_info.set_property("cmake_build_modules", [self._module_vars_file])
        self.cpp_info.set_property("cmake_file_name", "geotiff")
        self.cpp_info.set_property("cmake_target_name", "geotiff_library")

        self.cpp_info.names["cmake_find_package"] = "GeoTIFF"
        self.cpp_info.names["cmake_find_package_multi"] = "geotiff"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_vars_file]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_target_file]

        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
