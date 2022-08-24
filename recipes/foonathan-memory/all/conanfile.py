from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

class FoonathanMemory(ConanFile):

    name = "foonathan-memory"
    license = "Zlib"
    homepage = "https://github.com/foonathan/memory"
    url = "https://github.com/conan-io/conan-center-index"
    description = "STL compatible C++ memory allocator library"
    topics = ("conan", "memory", "STL", "RawAllocator")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared":          [True, False],
        "fPIC":            [True, False],
        "with_tools":      [True, False],
        "with_sizecheck":  [True, False]
    }
    default_options = {
        "shared":            False,
        "fPIC":              True,
        "with_tools":        True,
        "with_sizecheck":    True
    }
    generators = "cmake"
    short_paths = True
    exports_sources =  ["patches/**","CMakeLists.txt"]
    _cmake = None

    @property
    def _pkg_cmake(self):
        return os.path.join(
            self.package_folder,
            "lib",
            "foonathan_memory",
            "cmake"
        )
    
    @property
    def _pkg_share(self):
        return os.path.join(
            self.package_folder,
            "share"
        )

    @property
    def _module_subfolder(self):
        return os.path.join(
            "lib",
            "cmake"
        )

    @property
    def _module_file_rel_path(self):
        return os.path.join(
            self._module_subfolder,
            "conan-target-properties.cmake"
        )

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["FOONATHAN_MEMORY_BUILD_EXAMPLES"] = False
            self._cmake.definitions["FOONATHAN_MEMORY_BUILD_TESTS"] = False
            self._cmake.definitions["FOONATHAN_MEMORY_BUILD_TOOLS"] = self.options.with_tools
            self._cmake.definitions["FOONATHAN_MEMORY_CHECK_ALLOCATION_SIZE"] = self.options.with_sizecheck
            self._cmake.configure()
        return self._cmake

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
    
    def validate(self):
        # FIXME: jenkins servers throw error with this combination 
        # quick fix until somebody can reproduce
        if hasattr(self, "settings_build") and tools.cross_building(self):
            raise ConanInvalidConfiguration("Cross building is not yet supported. Contributions are welcome")
            raise ConanInvalidConfiguration("package currently do not support cross build to Macos armv8")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        tools.files.rmdir(self, self._pkg_cmake)
        tools.files.rmdir(self, self._pkg_share)
        tools.remove_files_by_mask(
            directory=os.path.join(self.package_folder, "lib"),
            pattern="*.pdb"
        )
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"foonathan_memory": "foonathan_memory::foonathan_memory"}
        )

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "foonathan_memory"
        self.cpp_info.names["cmake_find_package_multi"] = "foonathan_memory"
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.includedirs = [
            os.path.join("include", "foonathan_memory"),
            os.path.join("include", "foonathan_memory", "comp")
        ]
        if self.options.with_tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH env var with : {}".format(bin_path)),
            self.env_info.PATH.append(bin_path)

