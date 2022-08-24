from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


class XtensorConan(ConanFile):
    name = "xtensor"
    description = "C++ tensors with broadcasting and lazy computing"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xtensor-stack/xtensor"
    topics = ("numpy", "multidimensional-arrays", "tensors")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "xsimd": [True, False],
        "tbb": [True, False],
        "openmp": [True, False],
    }
    default_options = {
        "xsimd": True,
        "tbb": False,
        "openmp": False,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def requirements(self):
        self.requires("xtl/0.7.4")
        self.requires("nlohmann_json/3.10.5")
        if self.options.xsimd:
            if tools.Version(self.version) < "0.24.0":
                self.requires("xsimd/7.5.0")
            else:
                self.requires("xsimd/8.1.0")
        if self.options.tbb:
            self.requires("onetbb/2021.3.0")

    def validate(self):
        if self.options.tbb and self.options.openmp:
            raise ConanInvalidConfiguration(
                "The options 'tbb' and 'openmp' can not be used together."
            )

        # https://github.com/xtensor-stack/xtensor/blob/master/README.md
        # - On Windows platforms, Visual C++ 2015 Update 2, or more recent
        # - On Unix platforms, gcc 4.9 or a recent version of Clang
        version = tools.Version(self.settings.compiler.version)
        compiler = self.settings.compiler
        if compiler == "Visual Studio" and version < "16":
            raise ConanInvalidConfiguration(
                "xtensor requires at least Visual Studio version 15.9, please use 16"
            )
        if (compiler == "gcc" and version < "5.0") or (
            compiler == "clang" and version < "4"
        ):
            raise ConanInvalidConfiguration("xtensor requires at least C++14")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(
            "*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include")
        )

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"xtensor": "xtensor::xtensor"}
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
        self.cpp_info.set_property("cmake_file_name", "xtensor")
        self.cpp_info.set_property("cmake_target_name", "xtensor")
        self.cpp_info.set_property("pkg_config_name", "xtensor")
        if self.options.xsimd:
            self.cpp_info.defines.append("XTENSOR_USE_XSIMD")
        if self.options.tbb:
            self.cpp_info.defines.append("XTENSOR_USE_TBB")
        if self.options.openmp:
            self.cpp_info.defines.append("XTENSOR_USE_OPENMP")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
