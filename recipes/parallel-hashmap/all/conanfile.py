from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, save
from conan.tools.layout import basic_layout
import os
import textwrap

required_conan_version = ">=1.50.0"


class ParallelHashmapConan(ConanFile):
    name = "parallel-hashmap"
    description = "A family of header-only, very fast and memory-friendly hashmap and btree containers."
    license = "Apache-2.0"
    topics = ("parallel-hashmap", "parallel", "hashmap", "btree")
    homepage = "https://github.com/greg7mdp/parallel-hashmap"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "parallel_hashmap"),
                          dst=os.path.join(self.package_folder, "include", "parallel_hashmap"))
        copy(self, "phmap.natvis", src=self.source_folder, dst=os.path.join(self.source_folder, "res"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"phmap": "phmap::phmap"}
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
        self.cpp_info.set_property("cmake_file_name", "phmap")
        self.cpp_info.set_property("cmake_target_name", "phmap")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "phmap"
        self.cpp_info.names["cmake_find_package_multi"] = "phmap"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
