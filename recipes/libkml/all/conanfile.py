from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration
import functools
import os
import textwrap

required_conan_version = ">=1.43.0"


class LibkmlConan(ConanFile):
    name = "libkml"
    description = "Reference implementation of OGC KML 2.2"
    license = "BSD-3-Clause"
    topics = ("libkml", "kml", "ogc", "geospatial")
    homepage = "https://github.com/libkml/libkml"
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

    def requirements(self):
        self.requires("boost/1.78.0")
        self.requires("expat/2.4.8")
        self.requires("minizip/1.2.12")
        self.requires("uriparser/0.9.6")
        self.requires("zlib/1.2.12")

    def validate(self):
        if self.options.shared and \
           ((self.settings.compiler == "Visual Studio" and "MT" in self.settings.compiler.runtime) or \
            (self.settings.compiler == "msvc" and self.settings.compiler.runtime == "static")):
            raise ConanInvalidConfiguration("libkml shared with Visual Studio and MT runtime is not supported")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        # To install relocatable shared libs on Macos
        cmake.definitions["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {
                "kmlbase": "LibKML::kmlbase",
                "kmlxsd": "LibKML::kmlxsd",
                "kmldom": "LibKML::kmldom",
                "kmlengine": "LibKML::kmlengine",
                "kmlconvenience": "LibKML::kmlconvenience",
                "kmlregionator": "LibKML::kmlregionator",
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

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "LibKML")
        self.cpp_info.set_property("pkg_config_name", "libkml")

        self.cpp_info.names["cmake_find_package"] = "LibKML"
        self.cpp_info.names["cmake_find_package_multi"] = "LibKML"

        self._register_components({
            "kmlbase": {
                "defines": ["LIBKML_DLL"] if self.settings.os == "Windows" and self.options.shared else [],
                "system_libs": ["m"] if self.settings.os in ["Linux", "FreeBSD"] else [],
                "requires": ["boost::headers", "expat::expat", "minizip::minizip",
                             "uriparser::uriparser", "zlib::zlib"],
            },
            "kmlxsd": {
                "requires": ["boost::headers", "kmlbase"],
            },
            "kmldom": {
                "requires": ["boost::headers", "kmlbase"],
            },
            "kmlengine": {
                "system_libs": ["m"] if self.settings.os in ["Linux", "FreeBSD"] else [],
                "requires": ["boost::headers", "kmldom", "kmlbase"],
            },
            "kmlconvenience": {
                "requires": ["boost::headers", "kmlengine", "kmldom", "kmlbase"],
            },
            "kmlregionator": {
                "requires": ["kmlconvenience", "kmlengine", "kmldom", "kmlbase"],
            },
        })

    def _register_components(self, components):
        for comp_cmake_lib_name, values in components.items():
            defines = values.get("defines", [])
            system_libs = values.get("system_libs", [])
            requires = values.get("requires", [])
            self.cpp_info.components[comp_cmake_lib_name].set_property("cmake_target_name", comp_cmake_lib_name)
            self.cpp_info.components[comp_cmake_lib_name].names["cmake_find_package"] = comp_cmake_lib_name
            self.cpp_info.components[comp_cmake_lib_name].names["cmake_find_package_multi"] = comp_cmake_lib_name
            self.cpp_info.components[comp_cmake_lib_name].builddirs.append(self._module_subfolder)
            self.cpp_info.components[comp_cmake_lib_name].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components[comp_cmake_lib_name].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
            self.cpp_info.components[comp_cmake_lib_name].libs = [comp_cmake_lib_name]
            self.cpp_info.components[comp_cmake_lib_name].defines = defines
            self.cpp_info.components[comp_cmake_lib_name].system_libs = system_libs
            self.cpp_info.components[comp_cmake_lib_name].requires = requires
