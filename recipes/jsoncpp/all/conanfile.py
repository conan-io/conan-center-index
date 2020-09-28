from conans import ConanFile, CMake, tools
import os


class JsoncppConan(ConanFile):
    name = "jsoncpp"
    license = "MIT"
    homepage = "https://github.com/open-source-parsers/jsoncpp"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "json", "parser", "config")
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "jsoncpp-{}".format(self.version)
        os.rename(extracted_dir, self._source_subfolder)

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

        if tools.Version(self.version) >= "1.9.0":
            tools.replace_in_file(os.path.join(self._source_subfolder, "src", "lib_json", "CMakeLists.txt"),
                                  "$<BUILD_INTERFACE:${PROJECT_BINARY_DIR}/include/json>",
                                  "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["JSONCPP_WITH_TESTS"] = False
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
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        # TODO: CMake imported target shouldn't be namespaced (waiting https://github.com/conan-io/conan/issues/7615 to be implemented)
        self.cpp_info.names["cmake_find_package"] = "jsoncpp"
        self.cpp_info.names["cmake_find_package_multi"] = "jsoncpp"
        self.cpp_info.names["pkg_config"] = "jsoncpp"
        self.cpp_info.components["libjsoncpp"].names["cmake_find_package"] = "jsoncpp_lib"
        self.cpp_info.components["libjsoncpp"].names["cmake_find_package_multi"] = "jsoncpp_lib"
        self.cpp_info.components["libjsoncpp"].names["pkg_config"] = "jsoncpp"
        self.cpp_info.components["libjsoncpp"].libs = tools.collect_libs(self)
