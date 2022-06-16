from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


class XtensorBlasConan(ConanFile):
    name = "xtensor-blas"
    description = "Extension to the xtensor library, offering bindings to BLAS and LAPACK libraries through cxxblas and cxxlapack from the FLENS project."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xtensor-stack/xtensor-blas"
    topics = ("numpy", "multidimensional-arrays",
              "tensors", "openblas", "blas", "lapack")
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if tools.Version(self.version) == "0.17.2":
            self.requires("xtensor/0.21.4")
        else:
            self.requires("xtensor/0.24.0")
        self.requires("openblas/0.3.17")

    def validate(self):
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

    def configure(self):
        self.options["openblas"].build_lapack = True

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(
            pattern="*[.h|.hpp|.cxx]", dst="include", src=os.path.join(self._source_subfolder, "include")
        )

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"xtensor-blas": "xtensor-blas::xtensor-blas"}
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
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "xtensor-blas")
        self.cpp_info.set_property("cmake_target_name", "xtensor-blas")
        self.cpp_info.set_property("pkg_config_name", "xtensor-blas")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [
            self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [
            self._module_file_rel_path]
