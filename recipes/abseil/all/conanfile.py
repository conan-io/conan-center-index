from conans import ConanFile, CMake, tools
import json
import os
import re

required_conan_version = ">=1.33.0"


class ConanRecipe(ConanFile):
    name = "abseil"

    description = "Abseil Common Libraries (C++) from Google"
    topics = ("algorithm", "container", "google", "common", "utility")

    homepage = "https://github.com/abseil/abseil-cpp"
    url = "https://github.com/conan-io/conan-center-index"

    license = "Apache-2.0"

    exports_sources = ["CMakeLists.txt", "patches/**"]
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
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if not self.settings.compiler.cppstd:
            self._cmake.definitions["CMAKE_CXX_STANDARD"] = 11
        self._cmake.definitions["ABSL_ENABLE_INSTALL"] = True
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        cmake_folder = os.path.join(self.package_folder, "lib", "cmake")
        self._create_components_file_from_cmake_target_file(os.path.join(cmake_folder, "absl", "abslTargets.cmake"))
        tools.rmdir(cmake_folder)

    def _create_components_file_from_cmake_target_file(self, absl_target_file_path):
        components = {}

        abs_target_file = open(absl_target_file_path, "r")
        abs_target_content = abs_target_file.read()
        abs_target_file.close()

        cmake_functions = re.findall(r"(?P<func>add_library|set_target_properties)[\n|\s]*\([\n|\s]*(?P<args>[^)]*)\)", abs_target_content)
        for (cmake_function_name, cmake_function_args) in cmake_functions:
            cmake_function_args = re.split(r"[\s|\n]+", cmake_function_args, maxsplit=2)

            cmake_imported_target_name = cmake_function_args[0]
            cmake_target_nonamespace = cmake_imported_target_name.replace("absl::", "")
            potential_lib_name = "absl_" + cmake_target_nonamespace

            components.setdefault(potential_lib_name, {"cmake_target": cmake_target_nonamespace})

            if cmake_function_name == "add_library":
                cmake_imported_target_type = cmake_function_args[1]
                if cmake_imported_target_type in ["STATIC", "SHARED"]:
                    components[potential_lib_name]["libs"] = [potential_lib_name]
            elif cmake_function_name == "set_target_properties":
                target_properties = re.findall(r"(?P<property>INTERFACE_COMPILE_DEFINITIONS|INTERFACE_INCLUDE_DIRECTORIES|INTERFACE_LINK_LIBRARIES)[\n|\s]+(?P<values>.+)", cmake_function_args[2])
                for target_property in target_properties:
                    property_type = target_property[0]
                    if property_type == "INTERFACE_LINK_LIBRARIES":
                        values_list = target_property[1].replace('"', "").split(";")
                        for dependency in values_list:
                            if dependency.startswith("absl::"): # abseil targets
                                components[potential_lib_name].setdefault("requires", []).append(dependency.replace("absl::", "absl_"))
                            else: # system libs or frameworks
                                if self.settings.os == "Linux":
                                    if dependency == "Threads::Threads":
                                        components[potential_lib_name].setdefault("system_libs", []).append("pthread")
                                    elif "-lrt" in dependency:
                                        components[potential_lib_name].setdefault("system_libs", []).append("rt")
                                elif self.settings.os == "Windows":
                                    for system_lib in ["bcrypt", "advapi32", "dbghelp"]:
                                        if system_lib in dependency:
                                            components[potential_lib_name].setdefault("system_libs", []).append(system_lib)
                                elif self.settings.os == "Macos":
                                    for framework in ["CoreFoundation"]:
                                        if framework in dependency:
                                            components[potential_lib_name].setdefault("frameworks", []).append(framework)
                    elif property_type == "INTERFACE_COMPILE_DEFINITIONS":
                        values_list = target_property[1].replace('"', "").split(";")
                        for definition in values_list:
                            components[potential_lib_name].setdefault("defines", []).append(definition)

        # Save components informations in json file
        with open(self._components_helper_filepath, "w") as json_file:
            json.dump(components, json_file, indent=4)

    @property
    def _components_helper_filepath(self):
        return os.path.join(self.package_folder, "lib", "components.json")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "absl"
        self.cpp_info.names["cmake_find_package_multi"] = "absl"

        def _register_components():
            components_json_file = tools.load(self._components_helper_filepath)
            abseil_components = json.loads(components_json_file)
            for pkgconfig_name, values in abseil_components.items():
                cmake_target = values["cmake_target"]
                self.cpp_info.components[pkgconfig_name].names["cmake_find_package"] = cmake_target
                self.cpp_info.components[pkgconfig_name].names["cmake_find_package_multi"] = cmake_target
                self.cpp_info.components[pkgconfig_name].names["pkg_config"] = pkgconfig_name
                self.cpp_info.components[pkgconfig_name].libs = values.get("libs", [])
                self.cpp_info.components[pkgconfig_name].defines = values.get("defines", [])
                self.cpp_info.components[pkgconfig_name].system_libs = values.get("system_libs", [])
                self.cpp_info.components[pkgconfig_name].frameworks = values.get("frameworks", [])
                self.cpp_info.components[pkgconfig_name].requires = values.get("requires", [])

        _register_components()
