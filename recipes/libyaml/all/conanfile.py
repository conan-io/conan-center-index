from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, save
from conan.tools.microsoft import is_msvc
import os
import textwrap

required_conan_version = ">=1.47.0"


class LibYAMLConan(ConanFile):
    name = "libyaml"
    description = "LibYAML is a YAML parser and emitter library."
    topics = ("libyaml", "yaml", "parser", "emitter")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/yaml/libyaml"
    license = "MIT"

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
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
           del self.settings.compiler.libcxx
        except Exception:
           pass
        try:
           del self.settings.compiler.cppstd
        except Exception:
           pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["INSTALL_CMAKE_DIR"] = 'lib/cmake/libyaml'
        tc.variables["YAML_STATIC_LIB_NAME"] = "yaml"
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        # 0.2.2 has LICENSE, 0.2.5 has License, so ignore case
        copy(self, pattern="License", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"), ignore_case=True)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"yaml": "yaml::yaml"}
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
        self.cpp_info.set_property("cmake_file_name", "yaml")
        self.cpp_info.set_property("cmake_target_name", "yaml")
        self.cpp_info.libs = ["yaml"]
        if is_msvc(self):
            self.cpp_info.defines = [
                "YAML_DECLARE_EXPORT" if self.options.shared
                else "YAML_DECLARE_STATIC"
            ]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "yaml"
        self.cpp_info.names["cmake_find_package_multi"] = "yaml"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
