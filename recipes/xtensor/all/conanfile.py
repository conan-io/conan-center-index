from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.33.0"


class XtensorConan(ConanFile):
    name = "xtensor"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xtensor-stack/xtensor"
    description = "C++ tensors with broadcasting and lazy computing"
    topics = ("conan", "numpy", "multidimensional-arrays", "tensors")
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
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
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

    def requirements(self):
        self.requires("xtl/0.7.2")
        self.requires("nlohmann_json/3.9.1")
        if self.options.xsimd:
            self.requires("xsimd/7.4.10")
        if self.options.tbb:
            self.requires("tbb/2020.3")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(
            "*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include")
        )
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
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "xtensor"
        self.cpp_info.names["cmake_find_package_multi"] = "xtensor"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "xtensor"
        if self.options.xsimd:
            self.cpp_info.defines.append("XTENSOR_USE_XSIMD")
        if self.options.tbb:
            self.cpp_info.defines.append("XTENSOR_USE_TBB")
        if self.options.openmp:
            self.cpp_info.defines.append("XTENSOR_USE_OPENMP")
