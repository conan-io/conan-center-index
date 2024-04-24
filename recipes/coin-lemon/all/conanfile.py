from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, export_conandata_patches, get, patch, replace_in_file, rmdir
import os

required_conan_version = ">=1.53.0"


class CoinLemonConan(ConanFile):
    name = "coin-lemon"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://lemon.cs.elte.hu"
    description = "LEMON stands for Library for Efficient Modeling and Optimization in Networks."
    topics = ("data structures", "algorithms", "graphs", "network")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "unsupported_modern_cpp": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "unsupported_modern_cpp": False, # Do not set to True
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd") and not self.options.unsupported_modern_cpp:
            # This library does not support C++17 or higher, 
            # see: https://lemon.cs.elte.hu/trac/lemon/ticket/631
            #      it appears this library is no longer maintained
            try:
                from conan.tools.build import check_max_cppstd
                check_max_cppstd(self, 14)
            except ConanInvalidConfiguration:
                raise ConanInvalidConfiguration(f'Current cppstd {self.settings.compiler.cppstd} is'
                                                ' higher than supported (C++14)\n'
                                                ' Unverified support is available with the "coin-lemon/*:unsupported_modern_cpp=True" option')
            except ImportError:
                # Handle Conan 1.x (check_max_cppstd is not available)
                if self.settings.compiler.cppstd not in ["98", "gnu98", "11", "gnu11", "14", "gnu14"]:
                                    raise ConanInvalidConfiguration(f'Current cppstd {self.settings.compiler.cppstd} is'
                                                ' higher than supported (C++14)\n'
                                                ' Unverified support is available with the "coin-lemon/*:unsupported_modern_cpp=True" option')
        if self.options.unsupported_modern_cpp:
            self.output.warning("coin-lemon: Unsupported modern C++ patches are enabled. These are unverified.")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LEMON_ENABLE_GLPK"] = False
        tc.variables["LEMON_ENABLE_ILOG"] = False
        tc.variables["LEMON_ENABLE_COIN"] = False
        tc.variables["LEMON_ENABLE_SOPLEX"] = False
        # For msvc shared
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        # Relocatable shared libs on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        # For Ninja generator
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0058"] = "NEW"
        tc.generate()

    def _patch_sources(self):
        # Apply patches - note that some are conditional 
        for item in self.conan_data.get("patches", {}).get(self.version, []):
            if ('condition' in item and getattr(self.options, item['condition'])) or not 'condition' in item:
                patch(self, patch_file=item["patch_file"], patch_string=item.get("patch_description"))
        
        # Disable demo, tools, doc & test
        replace_in_file(
            self,
            os.path.join(self.source_folder, "CMakeLists.txt"),
            "IF(${CMAKE_SOURCE_DIR} STREQUAL ${PROJECT_SOURCE_DIR})",
            "if(0)",
        )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "LEMON")
        self.cpp_info.set_property("cmake_target_name", "LEMON::LEMON") # no official target name actually
        self.cpp_info.set_property("pkg_config_name", "lemon")
        self.cpp_info.libs = ["lemon" if self.settings.os == "Windows" else "emon"]
        self.cpp_info.defines.append("LEMON_ONLY_TEMPLATES")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "LEMON"
        self.cpp_info.names["cmake_find_package_multi"] = "LEMON"
        self.cpp_info.names["pkg_config"] = "lemon"
