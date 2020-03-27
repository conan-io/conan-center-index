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
    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    _source_subfolder = "source_subfolder"

    def configure(self):
        if self.settings.os == "Windows" or self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "jsoncpp-{}".format(self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "${jsoncpp_SOURCE_DIR}",
                              "${JSONCPP_SOURCE_DIR}")
        if self.settings.compiler == "Visual Studio" and self.settings.compiler.version == "11":
            tools.replace_in_file(os.path.join(self._source_subfolder, "include", "json", "value.h"),
                                  "explicit operator bool()",
                                  "operator bool()")

        if self.settings.os != "Windows" and not self.options.shared and not self.options.fPIC:
            tools.replace_in_file(os.path.join(self._source_subfolder, "src", "lib_json", "CMakeLists.txt"),
                                  "set_target_properties( jsoncpp_lib PROPERTIES POSITION_INDEPENDENT_CODE ON)",
                                  "set_target_properties( jsoncpp_lib PROPERTIES POSITION_INDEPENDENT_CODE OFF)")
        if tools.Version(self.version) > "1.9.0":
            tools.replace_in_file(os.path.join(self._source_subfolder, "src", "lib_json", "CMakeLists.txt"),
                                  "$<BUILD_INTERFACE:${PROJECT_BINARY_DIR}/include/json>",
                                  "")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "add_subdirectory( example )",
                              "",
                              strict=False)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["JSONCPP_WITH_TESTS"] = False
        cmake.definitions["JSONCPP_WITH_CMAKE_PACKAGE"] = False
        cmake.definitions["JSONCPP_WITH_STRICT_ISO"] = False
        cmake.definitions["JSONCPP_WITH_PKGCONFIG_SUPPORT"] = False
        cmake.configure()
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "JsonCpp"
        self.cpp_info.names["cmake_find_package_multi"] = "JsonCpp"
        self.cpp_info.libs = tools.collect_libs(self)
