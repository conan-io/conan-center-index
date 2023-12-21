from conan import ConanFile
from conan.tools.files import copy, get, save
from conan.tools.layout import basic_layout
import os
import textwrap

required_conan_version = ">=1.50.0"


class OpenclClhppHeadersConan(ConanFile):
    name = "opencl-clhpp-headers"
    description = "C++ language headers for the OpenCL API"
    license = "Apache-2.0"
    topics = ("opencl", "header-only", "api-headers")
    homepage = "https://github.com/KhronosGroup/OpenCL-CLHPP"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _target_name(self):
        return "OpenCL::HeadersCpp"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        self.requires(f"opencl-headers/{self.version}", transitive_headers=True)

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

    def generate(self):
        # TODO: to remove in conan v2 once legacy generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {self._target_name: f"{self.name}::{self.name}"}
        )

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=os.path.join(self.source_folder, "include", "CL"), dst=os.path.join(self.package_folder, "include", "CL"))

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenCLHeadersCpp")
        self.cpp_info.set_property("cmake_target_name", self._target_name)
        self.cpp_info.set_property("pkg_config_name", "OpenCL-CLHPP")
        self.cpp_info.requires = ["opencl-headers::opencl-headers"]
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "OpenCLHeadersCpp"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OpenCLHeadersCpp"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
