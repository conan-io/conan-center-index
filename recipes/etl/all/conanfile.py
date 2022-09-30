from conan import ConanFile
from conan.tools.files import get, copy, save
import os
import textwrap


required_conan_version = ">=1.50.0"


class EmbeddedTemplateLibraryConan(ConanFile):
    name = "etl"
    description = "A C++ template library for embedded applications"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.etlcpp.com/"
    topics = ("cpp", "embedded", "template", "container", "utility", "framework", "messaging")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            self,
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"etl": "etl::etl"}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(conanfile, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(conanfile, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "etl")
        self.cpp_info.set_property("cmake_target_name", "etl")

        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
