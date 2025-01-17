from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, save
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=2.1.0"


class XpropertyConan(ConanFile):
    name = "xproperty"
    description = "Traitlets-like C++ properties and implementation of the observer pattern."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jupyter-xeus/xproperty"
    topics = ("observer", "traitlets", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "14" if Version(self.version) <= "0.12.0" else "17"

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) < "0.12.0":
            self.requires("xtl/0.7.4", transitive_headers=True, transitive_libs=True)
        else:
            self.requires("nlohmann_json/3.11.3")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"xproperty": "xproperty::xproperty"}
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
        self.cpp_info.set_property("cmake_file_name", "xproperty")
        self.cpp_info.set_property("cmake_target_name", "xproperty")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
