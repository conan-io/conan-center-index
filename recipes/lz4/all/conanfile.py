from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir, save
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.50.0"


class LZ4Conan(ConanFile):
    name = "lz4"
    description = "Extremely Fast Compression algorithm"
    license = ("BSD-2-Clause", "BSD-3-Clause")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lz4/lz4"
    topics = ("lz4", "compression")

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
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LZ4_BUILD_CLI"] = False
        tc.variables["LZ4_BUILD_LEGACY_LZ4C"] = False
        tc.variables["LZ4_BUNDLED_MODE"] = False
        tc.variables["LZ4_POSITION_INDEPENDENT_LIB"] = self.options.get_safe("fPIC", True)
        # Generate a relocatable shared lib on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        # Honor BUILD_SHARED_LIBS (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    @property
    def _cmakelists_folder(self):
        if Version(self.version) < "1.9.3":
            subfolder = os.path.join("contrib", "cmake_unofficial")
        else:
            subfolder = os.path.join("build", "cmake")
        return os.path.join(self.source_folder, subfolder)

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=self._cmakelists_folder)
        cmake.build()

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        if Version(self.version) >= "1.9.4":
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        if Version(self.version) >= "1.9.4":
            # TODO: to remove in conan v2 once legacy generators removed
            self._create_cmake_module_alias_targets(
                os.path.join(self.package_folder, self._module_file_rel_path),
                {"lz4": "LZ4::lz4" if self.options.shared else "LZ4::lz4_static"}
            )

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "liblz4")
        if Version(self.version) >= "1.9.4":
            self.cpp_info.set_property("cmake_file_name", "LZ4")
            self.cpp_info.set_property("cmake_target_name", "LZ4::lz4" if self.options.shared else "LZ4::lz4_static")
        self.cpp_info.libs = ["lz4"]
        if is_msvc(self) and self.options.shared:
            self.cpp_info.defines.append("LZ4_DLL_IMPORT=1")
        self.cpp_info.names["pkg_config"] = "liblz4"

        if Version(self.version) >= "1.9.4":
            # TODO: to remove in conan v2 once legacy generators removed
            self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
