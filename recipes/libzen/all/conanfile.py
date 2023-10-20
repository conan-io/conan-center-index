from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save
import os
import textwrap

required_conan_version = ">=1.54.0"


class LibzenConan(ConanFile):
    name = "libzen"
    license = "ZLIB"
    homepage = "https://github.com/MediaArea/ZenLib"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Small C++ derivate classes to have an easier life"
    topics = ("c++", "helper", "util")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_unicode": [True, False],
        "enable_large_files": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_unicode": True,
        "enable_large_files": True,
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

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_UNICODE"] = self.options.enable_unicode
        tc.variables["LARGE_FILES"] = self.options.enable_large_files
        # Export symbols for msvc shared
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        # To install relocatable shared libs on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "Project", "CMake"))
        cmake.build()

    def package(self):
        copy(self, "License.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"zen": "ZenLib::ZenLib"}
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
        self.cpp_info.set_property("cmake_file_name", "ZenLib")
        self.cpp_info.set_property("cmake_target_name", "zen")
        self.cpp_info.set_property("pkg_config_name", "libzen")
        suffix = ""
        if self.settings.build_type == "Debug":
            if self.settings.os == "Windows":
                suffix = "d"
            elif is_apple_os(self):
                suffix = "_debug"
        self.cpp_info.libs = [f"zen{suffix}"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
        if self.options.enable_unicode:
            self.cpp_info.defines.extend(["UNICODE", "_UNICODE"])
        if self.options.shared:
            self.cpp_info.defines.append("LIBZEN_SHARED")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "ZenLib"
        self.cpp_info.names["cmake_find_package_multi"] = "ZenLib"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
