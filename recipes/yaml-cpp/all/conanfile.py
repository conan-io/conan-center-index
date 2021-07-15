import os
import textwrap
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class YamlCppConan(ConanFile):
    name = "yaml-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jbeder/yaml-cpp"
    topics = ("conan", "yaml", "yaml-parser", "serialization", "data-serialization")
    description = "A YAML parser and emitter in C++"
    license = "MIT"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

    def validate(self):
        if self.settings.compiler == "Visual Studio" and self.options.shared and "MT" in str(self.settings.compiler.runtime):
            raise ConanInvalidConfiguration("Visual Studio build for {} shared library with MT runtime is not supported".format(self.name))

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["YAML_CPP_BUILD_TESTS"] = False
        self._cmake.definitions["YAML_CPP_BUILD_CONTRIB"] = True
        self._cmake.definitions["YAML_CPP_BUILD_TOOLS"] = False
        self._cmake.definitions["YAML_CPP_INSTALL"] = True
        self._cmake.definitions["YAML_BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["YAML_MSVC_SHARED_RT"] = self.settings.compiler == "Visual Studio" and "MD" in str(self.settings.compiler.runtime)

        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # drop pc and cmake files
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "CMake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"yaml-cpp": "yaml-cpp::yaml-cpp"}
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
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.append("m")
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.defines.append("_NOEXCEPT=noexcept")
        self.cpp_info.names["cmake_find_package"] = "yaml-cpp"
        self.cpp_info.names["cmake_find_package_multi"] = "yaml-cpp"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.builddirs.append(self._module_subfolder)
