from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


class YamlCppConan(ConanFile):
    name = "yaml-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jbeder/yaml-cpp"
    topics = ("yaml", "yaml-parser", "serialization", "data-serialization")
    description = "A YAML parser and emitter in C++"
    license = "MIT"

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
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _is_vc_static_runtime(self):
        return (self.settings.compiler == "Visual Studio" and "MT" in self.settings.compiler.runtime) or \
               (str(self.settings.compiler) == "msvc" and self.settings.compiler.runtime == "static")

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

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "11")
        if self.options.shared and self._is_msvc and self._is_vc_static_runtime:
            raise ConanInvalidConfiguration("Visual Studio build for {} shared library with MT runtime is not supported".format(self.name))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

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
        if self._is_msvc:
            self._cmake.definitions["YAML_MSVC_SHARED_RT"] = not self._is_vc_static_runtime

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
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "CMake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
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
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "yaml-cpp")
        self.cpp_info.set_property("cmake_target_name", "yaml-cpp")
        self.cpp_info.set_property("pkg_config_name", "yaml-cpp")
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.append("m")
        if self._is_msvc:
            self.cpp_info.defines.append("_NOEXCEPT=noexcept")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
