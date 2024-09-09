from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import export_conandata_patches, apply_conandata_patches, copy, get, load, replace_in_file, rmdir, save
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import json
import os
import re
import textwrap

required_conan_version = ">=1.53.0"

class AbseilConan(ConanFile):
    name = "abseil"
    description = "Abseil Common Libraries (C++) from Google"
    topics = ("algorithm", "container", "google", "common", "utility")
    homepage = "https://github.com/abseil/abseil-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"

    package_type = "library"
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

    @property
    def _min_cppstd(self):
        return "11" if Version(self.version) < "20230125.0" else "14"

    @property
    def _compilers_minimum_version(self):
        return {
            "14": {
                "gcc": "6",
                "clang": "5",
                "apple-clang": "10",
                "Visual Studio": "15",
                "msvc": "191",
            },
        }.get(self._min_cppstd, {})

    def export_sources(self):
        copy(self, "abi_trick/*", self.recipe_folder, self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.options.shared and is_msvc(self) and Version(self.version) < "20230802.1":
            # upstream tries its best to export symbols, but it's broken for the moment
            raise ConanInvalidConfiguration(f"{self.ref} shared not availabe for Visual Studio, please use version 20230802.1 or newer")

    def build_requirements(self):
        # https://github.com/abseil/abseil-cpp/blob/20240722.0/CMakeLists.txt#L19
        if Version(self.version) >= "20240722.0":
            self.tool_requires("cmake/[>=3.16 <4]")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ABSL_ENABLE_INSTALL"] = True
        tc.variables["ABSL_PROPAGATE_CXX_STD"] = True
        tc.variables["BUILD_TESTING"] = False
        # We force CMP0067 policy to NEW for our abi trick in _patch_sources()
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0067"] = "NEW"
        if is_msvc(self):
            # see https://github.com/abseil/abseil-cpp/issues/649
            tc.preprocessor_definitions["_HAS_DEPRECATED_RESULT_OF"] = 1
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        # In case of cross-build, set CMAKE_SYSTEM_PROCESSOR if not set by toolchain or user
        if cross_building(self):
            toolchain_file = os.path.join(self.generators_folder, "conan_toolchain.cmake")
            cmake_system_processor_block = textwrap.dedent("""
                if(NOT CMAKE_SYSTEM_PROCESSOR)
                    set(CMAKE_SYSTEM_PROCESSOR {})
                endif()
            """.format(str(self.settings.arch)))
            save(self, toolchain_file, cmake_system_processor_block, append=True)

        # Trick to capture ABI
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        abi_trick_block = textwrap.dedent("""\
            list(APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/../abi_trick")
            include(conan_abi_test)
        """)
        save(self, cmakelists, abi_trick_block, append=True)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        abi_file = _ABIFile(self, os.path.join(self.build_folder, "abi.h"))
        abi_file.replace_in_options_file(os.path.join(self.source_folder, "absl", "base", "options.h"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        # Load components hierarchy before removing CMake files generated by abseil installation
        cmake_folder = os.path.join(self.package_folder, "lib", "cmake")
        absl_targets_file = os.path.join(cmake_folder, "absl", "abslTargets.cmake")
        components = self._load_components_from_cmake_target_file(absl_targets_file)
        rmdir(self, cmake_folder)

        # Create a json helper file in order to populate package_info() at consume time
        self._create_components_file(self._components_helper_filepath, components)

        # Create a build-module that will propagate the required cxx_std to consumers of this recipe's targets
        # TODO: Revisit with feedback from https://github.com/conan-io/conan/issues/10281
        self._create_cxx_std_module_file(self._cxx_std_module_filepath, components)

    def _load_components_from_cmake_target_file(self, absl_target_file_path):
        components = {}

        abs_target_content = load(self, absl_target_file_path)

        # Replace the line endings to support building with MSys2 on Windows
        abs_target_content = abs_target_content.replace("\r\n", "\n")

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
                    components[potential_lib_name]["libs"] = [potential_lib_name] if cmake_target_nonamespace != "abseil_dll" else ['abseil_dll']
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
                                elif is_apple_os(self):
                                    for framework in ["CoreFoundation"]:
                                        if framework in dependency:
                                            components[potential_lib_name].setdefault("frameworks", []).append(framework)
                    elif property_type == "INTERFACE_COMPILE_DEFINITIONS":
                        values_list = target_property[1].replace('"', "").split(";")
                        for definition in values_list:
                            if definition == r"\$<\$<PLATFORM_ID:AIX>:_LINUX_SOURCE_COMPAT>":
                                if self.settings.os == "AIX":
                                    components[potential_lib_name].setdefault("defines", []).append("_LINUX_SOURCE_COMPAT")
                            else:
                                components[potential_lib_name].setdefault("defines", []).append(definition)

        return components

    def _create_components_file(self, output_file, components):
        content = json.dumps(components, indent=4)
        save(self, output_file, content)

    @property
    def _components_helper_filepath(self):
        return os.path.join(self.package_folder, "lib", "components.json")

    def _create_cxx_std_module_file(self, output_file, components):
        content = ""
        cxx_std_required = _ABIFile(self, os.path.join(self.build_folder, "abi.h")).cxx_std()
        for _, values in components.items():
            cmake_target = values["cmake_target"]
            content += f"target_compile_features(absl::{cmake_target} INTERFACE cxx_std_{cxx_std_required})\n"
        save(self, output_file, content)

    @property
    def _cxx_std_module_filepath(self):
        return os.path.join(self.package_folder, "lib", "cmake", "conan_trick", "cxx_std.cmake")

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

            self.cpp_info.components[pkgconfig_name].names["cmake_find_package"] = cmake_target
            self.cpp_info.components[pkgconfig_name].names["cmake_find_package_multi"] = cmake_target

        self.cpp_info.names["cmake_find_package"] = "absl"
        self.cpp_info.names["cmake_find_package_multi"] = "absl"

        self.cpp_info.set_property("cmake_build_modules", [self._cxx_std_module_filepath])
        self.cpp_info.components["absl_config"].build_modules["cmake_find_package"] = [self._cxx_std_module_filepath]
        self.cpp_info.components["absl_config"].build_modules["cmake_find_package_multi"] = [self._cxx_std_module_filepath]


class _ABIFile:
    abi = {}

    def __init__(self, conanfile, filepath):
        self.conanfile = conanfile
        abi_h = load(self.conanfile, filepath)
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
