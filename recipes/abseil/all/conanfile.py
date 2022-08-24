from conan import ConanFile
from conan.tools.files import apply_conandata_patches, get, copy, rmdir, replace_in_file, load
from conan.tools.build import cross_building, check_min_cppstd
from conan.tools.microsoft import is_msvc
from conan.errors import ConanInvalidConfiguration
from conans import CMake
from conan.tools.apple import is_apple_os
import json
import os
import re
import functools


required_conan_version = ">=1.50.0"


class AbseilConan(ConanFile):
    name = "abseil"
    description = "Abseil Common Libraries (C++) from Google"
    topics = ("algorithm", "container", "google", "common", "utility")
    homepage = "https://github.com/abseil/abseil-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    short_paths = True
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        self.copy("abi.h.in")
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
            check_min_cppstd(self, 11)
        if self.options.shared and is_msvc(self):
            # upstream tries its best to export symbols, but it's broken for the moment
            raise ConanInvalidConfiguration("abseil shared not availabe for Visual Studio (yet)")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ABSL_ENABLE_INSTALL"] = True
        cmake.definitions["ABSL_PROPAGATE_CXX_STD"] = True
        cmake.definitions["BUILD_TESTING"] = False
        if cross_building(self):
            cmake.definitions["CONAN_ABSEIL_SYSTEM_PROCESSOR"] = str(self.settings.arch)
        cmake.configure()
        return cmake

    def build(self):
        apply_conandata_patches(self)
        cmake = self._configure_cmake()
        abi_file = _ABIFile(self, "abi.h")
        abi_file.replace_in_options_file(os.path.join(self._source_subfolder, "absl", "base", "options.h"))
        cmake.build()

    @property
    def _module_path(self):
        return os.path.join("lib", "cmake", "conan_trick")

    @property
    def _cxx_std_build_module(self):
        return "cxx_std.cmake"

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=os.path.join(self.build_folder, self._source_subfolder))
        cmake = self._configure_cmake()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        cmake_folder = os.path.join(self.package_folder, "lib", "cmake")
        components = self._create_components_file_from_cmake_target_file(os.path.join(cmake_folder, "absl", "abslTargets.cmake"))
        rmdir(self, cmake_folder)

        # Create a build-module that will propagate the required cxx_std to consumers of this recipe's targets
        # TODO: Revisit with feedback from https://github.com/conan-io/conan/issues/10281
        os.makedirs(os.path.join(self.package_folder, self._module_path))
        with open(os.path.join(self.package_folder, self._module_path, self._cxx_std_build_module), 'w', encoding='utf-8') as f:
            f.write("cmake_minimum_required(VERSION 3.1)\n\n")
            cxx_std_required = _ABIFile(self, "abi.h").cxx_std()
            for _, values in components.items():
                cmake_target = values["cmake_target"]
                f.write(f"target_compile_features(absl::{cmake_target} INTERFACE cxx_std_{cxx_std_required})\n")

    def _create_components_file_from_cmake_target_file(self, absl_target_file_path):
        components = {}

        abs_target_file = open(absl_target_file_path, "r", encoding="utf-8")
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
                    components[potential_lib_name]["libs"] = [potential_lib_name] if cmake_target_nonamespace != "abseil_dll" else []
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
                                if self.settings.os in ["Linux", "FreeBSD"]:
                                    if dependency == "Threads::Threads":
                                        components[potential_lib_name].setdefault("system_libs", []).append("pthread")
                                    elif "-lm" in dependency:
                                        components[potential_lib_name].setdefault("system_libs", []).append("m")
                                    elif "-lrt" in dependency:
                                        components[potential_lib_name].setdefault("system_libs", []).append("rt")
                                elif self.settings.os == "Windows":
                                    for system_lib in ["bcrypt", "advapi32", "dbghelp"]:
                                        if system_lib in dependency:
                                            components[potential_lib_name].setdefault("system_libs", []).append(system_lib)
                                elif is_apple_os(self.settings.os):
                                    for framework in ["CoreFoundation"]:
                                        if framework in dependency:
                                            components[potential_lib_name].setdefault("frameworks", []).append(framework)
                    elif property_type == "INTERFACE_COMPILE_DEFINITIONS":
                        values_list = target_property[1].replace('"', "").split(";")
                        for definition in values_list:
                            components[potential_lib_name].setdefault("defines", []).append(definition)

        # Save components informations in json file
        with open(self._components_helper_filepath, "w", encoding="utf-8") as json_file:
            json.dump(components, json_file, indent=4)

        return components

    @property
    def _components_helper_filepath(self):
        return os.path.join(self.package_folder, "lib", "components.json")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "absl")

        components_json_file = load(self, self._components_helper_filepath)
        abseil_components = json.loads(components_json_file)
        for pkgconfig_name, values in abseil_components.items():
            cmake_target = values["cmake_target"]
            self.cpp_info.components[pkgconfig_name].set_property("cmake_target_name", "absl::{}".format(cmake_target))
            self.cpp_info.components[pkgconfig_name].set_property("pkg_config_name", pkgconfig_name)
            self.cpp_info.components[pkgconfig_name].libs = values.get("libs", [])
            self.cpp_info.components[pkgconfig_name].defines = values.get("defines", [])
            self.cpp_info.components[pkgconfig_name].system_libs = values.get("system_libs", [])
            self.cpp_info.components[pkgconfig_name].frameworks = values.get("frameworks", [])
            self.cpp_info.components[pkgconfig_name].requires = values.get("requires", [])
            if is_msvc(self) and self.settings.compiler.get_safe("cppstd") == "20":
                self.cpp_info.components[pkgconfig_name].defines.extend(["_HAS_DEPRECATED_RESULT_OF", "_SILENCE_CXX17_RESULT_OF_DEPRECATION_WARNING"])

            self.cpp_info.components[pkgconfig_name].names["cmake_find_package"] = cmake_target
            self.cpp_info.components[pkgconfig_name].names["cmake_find_package_multi"] = cmake_target

        self.cpp_info.names["cmake_find_package"] = "absl"
        self.cpp_info.names["cmake_find_package_multi"] = "absl"

        cxx_std_build_module = os.path.join(self.package_folder, self._module_path, self._cxx_std_build_module)
        self.cpp_info.set_property("cmake_build_modules", [cxx_std_build_module, ])
        self.cpp_info.components["absl_config"].build_modules["cmake_find_package"] = [cxx_std_build_module, ]
        self.cpp_info.components["absl_config"].build_modules["cmake_find_package_multi"] = [cxx_std_build_module, ]


class _ABIFile:
    abi = {}

    def __init__(self, conanfile, filepath):
        self.conanfile = conanfile
        abi_h = load(self, filepath)
        for line in abi_h.splitlines():
            if line.startswith("#define"):
                tokens = line.split()
                if len(tokens) == 3:
                    self.abi[tokens[1]] = tokens[2]

    def replace_in_options_file(self, options_filepath):
        for name, value in self.abi.items():
            replace_in_file(self.conanfile, options_filepath,
                    "#define ABSL_OPTION_{} 2".format(name),
                    "#define ABSL_OPTION_{} {}".format(name, value))

    def cxx_std(self):
        return 17 if any([v == "1" for k, v in self.abi.items()]) else 11
