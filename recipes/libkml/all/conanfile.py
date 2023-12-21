from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os
import textwrap

required_conan_version = ">=1.54.0"


class LibkmlConan(ConanFile):
    name = "libkml"
    description = "Reference implementation of OGC KML 2.2"
    license = "BSD-3-Clause"
    topics = ("kml", "ogc", "geospatial")
    homepage = "https://github.com/libkml/libkml"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
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
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.81.0", transitive_headers=True)
        self.requires("expat/2.5.0")
        self.requires("minizip/1.2.13")
        self.requires("uriparser/0.9.7")
        self.requires("zlib/[>=1.2.11 <2]")

    def validate(self):
        if self.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration(f"{self.ref} shared with Visual Studio and MT runtime is not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        # To install relocatable shared libs on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "cmake"))
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
            self.cpp_info.components[comp_cmake_lib_name].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components[comp_cmake_lib_name].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
            self.cpp_info.components[comp_cmake_lib_name].libs = [comp_cmake_lib_name]
            self.cpp_info.components[comp_cmake_lib_name].defines = defines
            self.cpp_info.components[comp_cmake_lib_name].system_libs = system_libs
            self.cpp_info.components[comp_cmake_lib_name].requires = requires
