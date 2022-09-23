from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, get, rm, rmdir, save
import os
import textwrap

required_conan_version = ">=1.50.0"


class FoonathanMemoryConan(ConanFile):
    name = "foonathan-memory"
    license = "Zlib"
    homepage = "https://github.com/foonathan/memory"
    url = "https://github.com/conan-io/conan-center-index"
    description = "STL compatible C++ memory allocator library"
    topics = ("memory", "STL", "RawAllocator")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_tools": [True, False],
        "with_sizecheck":[True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_tools": True,
        "with_sizecheck": True,
    }

    short_paths = True

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        # FIXME: jenkins servers throw error with this combination
        # quick fix until somebody can reproduce
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("Cross building is not yet supported. Contributions are welcome")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FOONATHAN_MEMORY_BUILD_EXAMPLES"] = False
        tc.variables["FOONATHAN_MEMORY_BUILD_TESTS"] = False
        tc.variables["FOONATHAN_MEMORY_BUILD_TOOLS"] = self.options.with_tools
        tc.variables["FOONATHAN_MEMORY_CHECK_ALLOCATION_SIZE"] = self.options.with_sizecheck
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "foonathan_memory", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))

        # TODO: to remove in conan v2 once legacy generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"foonathan_memory": "foonathan_memory::foonathan_memory"},
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
        self.cpp_info.set_property("cmake_file_name", "foonathan_memory")
        self.cpp_info.set_property("cmake_target_name", "foonathan_memory")
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.includedirs = [os.path.join("include", "foonathan_memory")]

        if self.options.with_tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info(f"Appending PATH env var with : {bin_path}"),
            self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "foonathan_memory"
        self.cpp_info.names["cmake_find_package_multi"] = "foonathan_memory"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
