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

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if not tools.valid_min_cppstd(self, 11):
            self._cmake.definitions["CMAKE_CXX_STANDARD"] = 11
        self._cmake.definitions["ABSL_ENABLE_INSTALL"] = True
        self._cmake.definitions["BUILD_TESTING"] = False
        if tools.cross_building(self):
            self._cmake.definitions["CMAKE_SYSTEM_PROCESSOR"] = str(self.settings.arch)
        self._cmake.configure()
        return self._cmake

    @property
    def _abseil_abi_macros(self):
        return [
            "ABSL_OPTION_USE_STD_ANY",
            "ABSL_OPTION_USE_STD_OPTIONAL",
            "ABSL_OPTION_USE_STD_STRING_VIEW",
            "ABSL_OPTION_USE_STD_VARIANT",
        ]

    def _abseil_abi_config(self):
        """Determine the Abseil ABI for polyfills (absl::any, absl::optional, absl::string_view, and absl::variant)"""
        if self.settings.compiler.get_safe("cppstd"):
            if self.settings.compiler.get_safe("cppstd") >= "17":
                return "1"
            return "0"
        # As-of 2021-09-27 only GCC-11 defaults to C++17.
        if (
            self.settings.compiler == "gcc"
            and tools.Version(self.settings.compiler.version) >= "11"
        ):
            return "1"
        return "0"

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        absl_option = self._abseil_abi_config()
        for macro in self._abseil_abi_macros:
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "absl", "base", "options.h"),
                "#define {} 2".format(macro),
                "#define {} {}".format(macro, absl_option),
            )
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
                if self.settings.compiler == "Visual Studio" and self.settings.get_safe("compiler.cppstd") == "20":
                    self.cpp_info.components[pkgconfig_name].defines.extend(["_HAS_DEPRECATED_RESULT_OF", "_SILENCE_CXX17_RESULT_OF_DEPRECATION_WARNING"])

        _register_components()
