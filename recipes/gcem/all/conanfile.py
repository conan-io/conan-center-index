from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, save
from conan.tools.layout import basic_layout
import os
import textwrap

required_conan_version = ">=1.50.0"


class GcemConan(ConanFile):
    name = "gcem"
    description = "A C++ compile-time math library using generalized " \
                  "constant expressions."
    license = "Apache-2.0"
    topics = ("gcem", "math", "header-only")
    homepage = "https://github.com/kthohr/gcem"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True
    settings = "os", "arch", "compiler", "build_type",

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

        # TODO: to remove in conan v2
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"gcem": "gcem::gcem"},
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
        self.cpp_info.set_property("cmake_file_name", "gcem")
        self.cpp_info.set_property("cmake_target_name", "gcem")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
