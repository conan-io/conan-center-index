import glob
import json
import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration, ConanException


class ConanRecipe(ConanFile):
    name = "abseil"

    description = "Abseil Common Libraries (C++) from Google"
    topics = ("algorithm", "container", "google", "common", "utility")

    homepage = "https://github.com/abseil/abseil-cpp"
    url = "https://github.com/conan-io/conan-center-index"

    license = "Apache-2.0"

    exports = "components/**"
    generators = "cmake"
    short_paths = True

    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob('abseil-cpp-*/')[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ABSL_ENABLE_INSTALL"] = True
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "project(absl CXX)", """project(absl CXX)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()""")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "absl"
        self.cpp_info.names["cmake_find_package_multi"] = "absl"
        self._register_components()

    def _register_components(self):
        components_json_filepath = os.path.join(self.recipe_folder, "components", "components_{}.json".format(self.version))
        with open(components_json_filepath) as components_json_file:
            abseil_components = json.load(components_json_file)
            for component in abseil_components:
                self._register_component(component)

    def _register_component(self, component):
        conan_name = component["conan_name"]
        cmake_target = component["cmake_target"]
        self.cpp_info.components[conan_name].names["cmake_find_package"] = cmake_target
        self.cpp_info.components[conan_name].names["cmake_find_package_multi"] = cmake_target
        self.cpp_info.components[conan_name].libs = component.get("libs", [])
        self.cpp_info.components[conan_name].defines = component.get("defines", [])
        self.cpp_info.components[conan_name].system_libs = component.get("system_libs", {}).get(str(self.settings.os), [])
        self.cpp_info.components[conan_name].frameworks = component.get("frameworks", [])
        self.cpp_info.components[conan_name].requires = component.get("requires", [])
