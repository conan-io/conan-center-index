from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir, save
from conan.tools.scm import Version

import os
import textwrap

required_conan_version = ">=1.53.0"


class AwsCMQTT(ConanFile):
    name = "aws-c-mqtt"
    description = "C99 implementation of the MQTT 3.1.1 specification."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-mqtt"
    topics = ("aws", "amazon", "cloud", "mqtt")
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("aws-c-common/0.8.2", transitive_headers=True, transitive_libs=True)
        self.requires("aws-c-cal/0.5.13")
        if Version(self.version) < "0.7.12":
            self.requires("aws-c-io/0.10.20", transitive_headers=True)
            self.requires("aws-c-http/0.6.13")
        else:
            self.requires("aws-c-io/0.13.4", transitive_headers=True)
            self.requires("aws-c-http/0.6.22")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-c-mqtt"))

        # TODO: to remove in conan v2 once legacy generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"AWS::aws-c-mqtt": "aws-c-mqtt::aws-c-mqtt"}
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-c-mqtt")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-mqtt")
        self.cpp_info.libs = ["aws-c-mqtt"]
        if self.options.shared:
            self.cpp_info.defines.append("AWS_MQTT_USE_IMPORT_EXPORT")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
