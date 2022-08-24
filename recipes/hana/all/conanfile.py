from conan import ConanFile, tools$
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.33.0"


class HanaConan(ConanFile):
    name = "hana"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://boostorg.github.io/hana/"
    description = "Hana is a header-only library for C++ metaprogramming suited for computations on both types and values."
    license = "BSL-1.0"
    topics = ("hana", "metaprogramming", "boost")
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "_source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "Visual Studio": "14",
            "clang": "3.4",
            "apple-clang": "3.4",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, "14")

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("{} {} requires C++14. Your compiler is unknown. Assuming it supports C++14.".format(self.name, self.version))
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration("{} {} requires C++14, which your compiler does not support.".format(self.name, self.version))

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"hana": "hana::hana"}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.files.save(self, module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "Hana"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Hana"
        self.cpp_info.names["cmake_find_package"] = "hana"
        self.cpp_info.names["cmake_find_package_multi"] = "hana"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "hana"
