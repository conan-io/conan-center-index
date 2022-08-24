from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


class XtlConan(ConanFile):
    name = "xtl"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xtensor-stack/xtl"
    description = "The x template library"
    topics = ("templates", "containers", "algorithms")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, "14")

        minimum_version = {
            "clang": "3.9",
            "gcc": "6",
            "Visual Studio": "15.0",
        }.get(str(self.settings.compiler))

        if not minimum_version:
            self.output.warn(
                "Unknown compiler {} {}. Assuming compiler supports C++14."
                .format(self.settings.compiler, self.settings.compiler.version))
        else:
            version = tools.scm.Version(self.settings.compiler.version)
            if version < minimum_version:
                raise ConanInvalidConfiguration(
                    "The compiler {} {} does not support C++14."
                    .format(self.settings.compiler, self.settings.compiler.version))

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"xtl": "xtl::xtl"}
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
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "xtl")
        self.cpp_info.set_property("cmake_target_name", "xtl")
        self.cpp_info.set_property("pkg_config_name", "xtl")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
