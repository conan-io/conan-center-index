from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

class FastCDRConan(ConanFile):

    name = "foonathan-memory"
    version = "0.7.0"
    license = "Zlib"
    homepage = "https://github.com/eProsima/Fast-CDR"
    url = "https://github.com/conan-io/conan-center-index"
    description = "eProsima FastCDR library for serialization"
    topics = ("conan", "DDS", "Middleware", "Serialization")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared":          [True, False],
        "fPIC":            [True, False]
    }
    default_options = {
        "shared":            False,
        "fPIC":              True
    }
    generators = "cmake"
    exports_sources = ["CMakeLists.txt"]
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

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["BUILD_MEMORY_EXAMPLES"] = False
            self._cmake.definitions["BUILD_MEMORY_TOOLS"] = False
            self._cmake.definitions["BUILD_MEMORY_TOOLS"] = False
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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        tools.rmdir(self._pkg_cmake)
        tools.remove_files_by_mask(
            directory=os.path.join(self.package_folder, "lib"),
            pattern="*.pdb"
        )
        tools.remove_files_by_mask(
            directory=os.path.join(self.package_folder, "bin"),
            pattern="*.pdb"
        )
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"foonathan_memory": "foonathan_memory::foonathan_memory"}
        )

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "foonathan_memory "
        self.cpp_info.names["cmake_find_package_multi"] = "foonathan_memory "
        self.cpp_info.libs = tools.collect_libs(self)
