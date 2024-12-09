from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools import build, files
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.scm import Version
import json
import os
import re

required_conan_version = ">=1.52.0"

class NmosCppConan(ConanFile):
    name = "nmos-cpp"
    description = "An NMOS C++ Implementation"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/sony/nmos-cpp"
    topics = ("amwa", "nmos", "is-04", "is-05", "is-07", "is-08", "is-09", "broadcasting", "network", "media")

    # https://github.com/sony/nmos-cpp/blob/master/Development/cmake/NmosCppLibraries.cmake#L947
    package_type = "static-library"
    settings = "os", "compiler", "build_type", "arch"
    # for now, no "shared" option support
    options = {
        "fPIC": [True, False],
        "with_dnssd": ["mdnsresponder", "avahi"],
    }
    # "fPIC" is handled automatically by Conan, injecting CMAKE_POSITION_INDEPENDENT_CODE
    default_options = {
        "fPIC": True,
        "with_dnssd": "mdnsresponder",
    }

    short_paths = True

    def export_sources(self):
        files.export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if self.settings.os == "Macos":
            del self.options.with_dnssd
        elif self.settings.os == "Linux":
            self.options.with_dnssd = "avahi"
        elif self.settings.os == "Windows":
            self.options.with_dnssd = "mdnsresponder"

    def requirements(self):
        # for now, consistent with project's conanfile.txt
        # INFO: details/system_error.h: #include <boost/system/system_error.hpp>
        self.requires("boost/1.83.0", transitive_headers=True)
        # INFO: json_ops.h exposes cpprest/json.h
        self.requires("cpprestsdk/2.10.19", transitive_headers=True)
        self.requires("websocketpp/0.8.2")
        self.requires("openssl/[>=1.1 <4]")
        self.requires("json-schema-validator/2.3.0")
        self.requires("nlohmann_json/3.11.3")
        if Version(self.version) >= "cci.20240222":
            self.requires("jwt-cpp/0.7.0")

        if self.options.get_safe("with_dnssd") == "mdnsresponder":
            self.requires("mdnsresponder/878.200.35")
            # The option mdnsresponder:with_opt_patches=True is recommended in order to permit the
            # over-long service type _nmos-registration._tcp used in IS-04 v1.2, and also to enable
            # support for unicast DNS-SD on Linux, since NMOS recommends this in preference to mDNS.
            # See https://specs.amwa.tv/is-04/releases/v1.3.1/docs/3.1._Discovery_-_Registered_Operation.html#dns-sd-advertisement
        elif self.options.get_safe("with_dnssd") == "avahi":
            self.requires("avahi/0.8")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.17 <4]")

    def validate(self):
        if self.info.settings.os in ["Macos"]:
            raise ConanInvalidConfiguration(f"{self.ref} is not currently supported on {self.info.settings.os}. Contributions welcomed.")
        if self.info.settings.compiler.get_safe("cppstd"):
            build.check_min_cppstd(self, 11)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)
        files.rm(self, "conanfile.txt", os.path.join(self.source_folder, "Development"))

    def generate(self):
        tc = CMakeToolchain(self)
        # prefer config-file packages created by cmake_find_package_multi
        # over any system-installed find-module packages
        tc.cache_variables["CMAKE_FIND_PACKAGE_PREFER_CONFIG"] = True
        # disable cmake-conan, consume conan packages in local cache to avoid incompatible requirements
        # between this recipe and project's conanfile.txt
        tc.cache_variables["CONAN_EXPORTED"] = True
        # (on Linux) select Avahi or mDNSResponder
        tc.variables["NMOS_CPP_USE_AVAHI"] = self.options.get_safe("with_dnssd") == "avahi"
        # (on Windows) use the Conan package for DNSSD (mdnsresponder), not the project's own DLL stub library
        tc.variables["NMOS_CPP_USE_BONJOUR_SDK"] = True
        # no need to build unit tests
        tc.variables["NMOS_CPP_BUILD_TESTS"] = False
        # the examples (nmos-cpp-registry and nmos-cpp-node) are useful utilities for users
        tc.variables["NMOS_CPP_BUILD_EXAMPLES"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        files.apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder="Development")
        cmake.build()

    def package(self):
        files.copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        cmake_folder = os.path.join(self.package_folder, "lib", "cmake")
        self._create_components_file_from_cmake_target_file(os.path.join(cmake_folder, "nmos-cpp", "nmos-cpp-targets.cmake"))
        # remove the project's own generated config-file package
        files.rmdir(self, cmake_folder)

    def _create_components_file_from_cmake_target_file(self, target_file_path):
        components = {}

        target_content = files.load(self, target_file_path)

        cmake_functions = re.findall(r"(?P<func>add_executable|add_library|set_target_properties)[\n|\s]*\([\n|\s]*(?P<args>[^)]*)\)", target_content)
        for (cmake_function_name, cmake_function_args) in cmake_functions:
            cmake_function_args = re.split(r"[\s|\n]+", cmake_function_args, maxsplit=2)

            cmake_imported_target_name = cmake_function_args[0]
            cmake_target_nonamespace = cmake_imported_target_name.replace("nmos-cpp::", "")
            component_name = cmake_target_nonamespace.lower()
            # Conan component name cannot be the same as the package name
            if component_name == "nmos-cpp":
                component_name = "nmos-cpp-lib"

            components.setdefault(component_name, {"cmake_target": cmake_target_nonamespace})

            if cmake_function_name == "add_executable":
                components[component_name]["exe"] = True
            elif cmake_function_name == "add_library":
                cmake_imported_target_type = cmake_function_args[1]
                if cmake_imported_target_type in ["STATIC", "SHARED"]:
                    # library filenames are based on the target name by default
                    lib_name = cmake_target_nonamespace
                    # the filename may be changed by a straightforward command:
                    # set_property(TARGET Bonjour PROPERTY OUTPUT_NAME dnssd)
                    # but we'd have to read the nmos-cpp-targets-<config>.cmake files
                    # and parse the IMPORTED_LOCATION_<CONFIG> values
                    if lib_name == "Bonjour":
                        lib_name = "dnssd"
                    components[component_name]["libs"] = [lib_name]
            elif cmake_function_name == "set_target_properties":
                target_properties = re.findall(r"(?P<property>INTERFACE_[A-Z_]+)[\n|\s]+\"(?P<values>.+)\"", cmake_function_args[2])
                for target_property in target_properties:
                    property_type = target_property[0]
                    # '\', '$' and '"' are escaped; '$' especially is important here
                    # see https://github.com/conan-io/conan/blob/release/1.39/conans/client/generators/cmake_common.py#L43-L48
                    property_values = re.sub(r"\\(.)", r"\1", target_property[1]).split(";")
                    if property_type == "INTERFACE_LINK_LIBRARIES":
                        for dependency in property_values:
                            match_private = re.fullmatch(r"\$<LINK_ONLY:(.+)>", dependency)
                            if match_private:
                                dependency = match_private.group(1)
                            # target dependencies can be treated fairly consistently
                            if "::" in dependency or dependency in ["nlohmann_json_schema_validator"]:
                                dependency = dependency.replace("nmos-cpp::", "")
                                # Conan component name cannot be the same as the package name
                                if dependency == "nmos-cpp":
                                    dependency = "nmos-cpp-lib"
                                # Conan packages for Boost, cpprestsdk, websocketpp, OpenSSL and Avahi have component names that (except for being lowercase) match the CMake targets
                                # json-schema-validator overrides cmake_find_package[_multi] names and v2 cmake_target_name
                                elif dependency == "nlohmann_json_schema_validator":
                                    dependency = "json-schema-validator::json-schema-validator"
                                # mdnsresponder overrides cmake_find_package[_multi] names
                                elif dependency == "DNSSD::DNSSD":
                                    dependency = "mdnsresponder::mdnsresponder"
                                components[component_name].setdefault("requires" if not match_private else "requires_private", []).append(dependency.lower())
                            elif "${_IMPORT_PREFIX}/lib/" in dependency:
                                self.output.warn(f"{self.name} recipe does not handle {property_type} {dependency} (yet)")
                            else:
                                components[component_name].setdefault("system_libs", []).append(dependency)
                    elif property_type == "INTERFACE_COMPILE_DEFINITIONS":
                        for property_value in property_values:
                            components[component_name].setdefault("defines", []).append(property_value)
                    elif property_type == "INTERFACE_COMPILE_FEATURES":
                        for property_value in property_values:
                            if property_value not in ["cxx_std_11"]:
                                self.output.warn(f"{self.name} recipe does not handle {property_type} {property_value} (yet)")
                    elif property_type == "INTERFACE_COMPILE_OPTIONS":
                        for property_value in property_values:
                            # handle forced include (Visual Studio /FI, gcc -include) by relying on includedirs containing "include"
                            property_value = property_value.replace("${_IMPORT_PREFIX}/include/", "")
                            components[component_name].setdefault("cxxflags", []).append(property_value)
                    elif property_type == "INTERFACE_INCLUDE_DIRECTORIES":
                        for property_value in property_values:
                            if property_value not in ["${_IMPORT_PREFIX}/include"]:
                                self.output.warn(f"{self.name} recipe does not handle {property_type} {property_value} (yet)")
                    elif property_type == "INTERFACE_LINK_OPTIONS":
                        for property_value in property_values:
                            # workaround required because otherwise "/ignore:4099" gets converted to "\ignore:4099.obj"
                            # thankfully the MSVC linker accepts both '/' and '-' for the option specifier and Visual Studio
                            # handles link options appearing in Link/AdditionalDependencies rather than Link/AdditionalOptions
                            # because the CMake generators put them in INTERFACE_LINK_LIBRARIES rather than INTERFACE_LINK_OPTIONS
                            # see https://github.com/conan-io/conan/pull/8812
                            # and https://docs.microsoft.com/en-us/cpp/build/reference/linking?view=msvc-160#command-line
                            property_value = re.sub(r"^/", r"-", property_value)
                            components[component_name].setdefault("linkflags", []).append(property_value)
                    else:
                        self.output.warn(f"{self.name} recipe does not handle {property_type} (yet)")

        # until https://github.com/sony/nmos-cpp/commit/9489d84098ddc8cc514b7e4d5afe740dee4518ee
        # direct dependency on nlohmann_json was missing
        if Version(self.version) < "cci.20221203":
            components["json_schema_validator"].setdefault("requires", []).append("nlohmann_json::nlohmann_json")

        # Save components informations in json file
        with open(self._components_helper_filepath, "w", encoding="utf-8") as json_file:
            json.dump(components, json_file, indent=4)

    @property
    def _components_helper_filepath(self):
        return os.path.join(self.package_folder, "lib", "components.json")

    def package_info(self):
        bindir = "bin"
        libdir = "lib"
        # on Windows, cmake_install() puts the binaries in a config-specific sub-folder
        if self.settings.os == "Windows":
            config_install_dir = "Debug" if self.settings.build_type == "Debug" else "Release"
            bindir = os.path.join(bindir, config_install_dir)
            libdir = os.path.join(libdir, config_install_dir)
        self.cpp_info.bindirs = [bindir]
        self.cpp_info.libdirs = [libdir]

        def _register_components():
            components_json_file = files.load(self, self._components_helper_filepath)
            components = json.loads(components_json_file)
            for component_name, values in components.items():
                cmake_target = values["cmake_target"]
                self.cpp_info.components[component_name].names["cmake_find_package"] = cmake_target
                self.cpp_info.components[component_name].names["cmake_find_package_multi"] = cmake_target
                self.cpp_info.components[component_name].bindirs = [bindir] if values.get("exe") else []
                self.cpp_info.components[component_name].libs = values.get("libs", [])
                self.cpp_info.components[component_name].libdirs = [libdir]
                self.cpp_info.components[component_name].defines = values.get("defines", [])
                self.cpp_info.components[component_name].cxxflags = values.get("cxxflags", [])
                linkflags = values.get("linkflags", [])
                self.cpp_info.components[component_name].sharedlinkflags = linkflags
                self.cpp_info.components[component_name].exelinkflags = linkflags
                self.cpp_info.components[component_name].system_libs = values.get("system_libs", [])
                self.cpp_info.components[component_name].frameworks = values.get("frameworks", [])
                self.cpp_info.components[component_name].requires = values.get("requires", [])
                # hmm, how should private requirements be indicated? this results in a string format error...
                #self.cpp_info.components[component_name].requires.extend([(r, "private") for r in values.get("requires_private", [])])
                self.cpp_info.components[component_name].requires.extend(values.get("requires_private", []))
        _register_components()

        # add nmos-cpp-registry and nmos-cpp-node to the path
        bin_path = os.path.join(self.package_folder, bindir)
        self.env_info.PATH.append(bin_path)
