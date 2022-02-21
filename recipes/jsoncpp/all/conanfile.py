from conans import ConanFile, CMake, tools
import os
import textwrap

required_conan_version = ">=1.33.0"

class JsoncppConan(ConanFile):
    name = "jsoncpp"
    license = "MIT"
    homepage = "https://github.com/open-source-parsers/jsoncpp"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("json", "parser", "config")
    description = "A C++ library for interacting with JSON."
    settings = "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "${jsoncpp_SOURCE_DIR}",
                              "${JSONCPP_SOURCE_DIR}")
        if self.settings.compiler == "Visual Studio" and self.settings.compiler.version == "11":
            tools.replace_in_file(os.path.join(self._source_subfolder, "include", "json", "value.h"),
                                  "explicit operator bool()",
                                  "operator bool()")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["JSONCPP_WITH_TESTS"] = False
        self._cmake.definitions["JSONCPP_WITH_WARNING_AS_ERROR"] = False
        self._cmake.definitions["JSONCPP_WITH_CMAKE_PACKAGE"] = False
        self._cmake.definitions["JSONCPP_WITH_STRICT_ISO"] = False
        self._cmake.definitions["JSONCPP_WITH_PKGCONFIG_SUPPORT"] = False
        jsoncpp_version = tools.Version(self.version)
        if jsoncpp_version < "1.9.0" or jsoncpp_version >= "1.9.4":
            self._cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
        if jsoncpp_version >= "1.9.3":
            self._cmake.definitions["JSONCPP_WITH_EXAMPLE"] = False
        if jsoncpp_version >= "1.9.4":
            self._cmake.definitions["BUILD_OBJECT_LIBS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {
                "jsoncpp_lib": "jsoncpp::jsoncpp",        # imported target for shared lib, but also static between 1.9.0 & 1.9.3
                "jsoncpp_static": "jsoncpp::jsoncpp",     # imported target for static lib if >= 1.9.4
                "jsoncpp_lib_static": "jsoncpp::jsoncpp", # imported target for static lib if < 1.9.0
            }
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
        self.cpp_info.names["cmake_find_package"] = "jsoncpp"
        self.cpp_info.names["cmake_find_package_multi"] = "jsoncpp"
        self.cpp_info.names["pkg_config"] = "jsoncpp"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("JSON_DLL")
