from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"


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
        self.requires("expat/[>=2.6.2 <3]")
        self.requires("minizip/1.2.13")
        self.requires("uriparser/0.9.7")
        self.requires("zlib/[>=1.2.11 <2]")

    def validate(self):
        if self.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration(f"{self.ref} shared with Visual Studio and MT runtime is not supported")

    def package_id(self):
        cppstd = self.info.settings.get_safe("compiler.cppstd")
        if cppstd and cppstd not in ['98', 'gnu98', '11', 'gnu11', '14', 'gnu14']:
            prefix = "gnu" if str(cppstd).startswith("gnu") else ""
            self.info.settings.compiler.cppstd = f"{prefix}14"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True

        # Fallback to C++14 - the implementation uses
        # functionality that is not compliant with C++17
        # See https://github.com/conan-io/conan/issues/16148
        cppstd = self.settings.get_safe("compiler.cppstd")
        if cppstd and conan_version.major >= 2:
            from conan.tools.build import valid_max_cppstd
            if not valid_max_cppstd(self, "14"):
                self.output.warning(f"Recipe not compatible with C++ {cppstd}, falling back to C++14")
                use_gnu_extensions = str(cppstd).startswith("gnu")
                tc.blocks.remove("cppstd")
                tc.cache_variables["CMAKE_CXX_STANDARD"] = "14"
                tc.cache_variables["CMAKE_CXX_EXTENSIONS"] = use_gnu_extensions

        # To install relocatable shared libs on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5" # CMake 4 support
        if Version(self.version) > "1.3.0": # pylint: disable=conan-unreachable-upper-version
            raise ConanException("CMAKE_POLICY_VERSION_MINIMUM hardcoded to 3.5, check if new version supports CMake 4")
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

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "LibKML")
        self.cpp_info.set_property("pkg_config_name", "libkml")

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
            self.cpp_info.components[comp_cmake_lib_name].libs = [comp_cmake_lib_name]
            self.cpp_info.components[comp_cmake_lib_name].defines = defines
            self.cpp_info.components[comp_cmake_lib_name].system_libs = system_libs
            self.cpp_info.components[comp_cmake_lib_name].requires = requires
