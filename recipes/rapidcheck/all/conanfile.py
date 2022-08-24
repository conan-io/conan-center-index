from from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import functools
import textwrap

required_conan_version = ">=1.43.0"


class RapidcheckConan(ConanFile):
    name = "rapidcheck"
    description = "QuickCheck clone for C++ with the goal of being simple to use with as little boilerplate as possible"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/emil-e/rapidcheck"
    license = "BSD-2-Clause"
    topics = ("quickcheck", "testing", "property-testing")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_rtti": [True, False],
        "enable_catch": [True, False],
        "enable_gmock": [True, False],
        "enable_gtest": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_rtti": True,
        "enable_catch": False,
        "enable_gmock": False,
        "enable_gtest": False,
    }

    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.enable_catch:
            self.requires("catch2/2.13.9")
        if self.options.enable_gmock or self.options.enable_gtest:
            self.requires("gtest/1.11.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        if self._is_msvc and self.options.shared:
            raise ConanInvalidConfiguration("shared is not supported using Visual Studio")
        if self.options.enable_gmock and not self.deps_cpp_info["gtest"].build_gmock:
            raise ConanInvalidConfiguration("The option `rapidcheck:enable_gmock` requires gtest:build_gmock=True`")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["RC_ENABLE_RTTI"] = self.options.enable_rtti
        cmake.definitions["RC_ENABLE_TESTS"] = False
        cmake.definitions["RC_ENABLE_EXAMPLES"] = False
        cmake.definitions["RC_ENABLE_CATCH"] = self.options.enable_catch
        cmake.definitions["RC_ENABLE_GMOCK"] = self.options.enable_gmock
        cmake.definitions["RC_ENABLE_GTEST"] = self.options.enable_gtest
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {
                "rapidcheck": "rapidcheck::rapidcheck_rapidcheck",
                "rapidcheck_catch":"rapidcheck::rapidcheck_catch",
                "rapidcheck_gmock": "rapidcheck::rapidcheck_gmock",
                "rapidcheck_gtest": "rapidcheck::rapidcheck_gtest",
            }
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
        self.cpp_info.set_property("cmake_file_name", "rapidcheck")

        self.cpp_info.components["rapidcheck_rapidcheck"].set_property("cmake_target_name", "rapidcheck")
        self.cpp_info.components["rapidcheck_rapidcheck"].libs = ["rapidcheck"]
        version = str(self.version)[4:]
        if tools.Version(version) < "20201218":
            if self.options.enable_rtti:
                self.cpp_info.components["rapidcheck_rapidcheck"].defines.append("RC_USE_RTTI")
        else:
            if not self.options.enable_rtti:
                self.cpp_info.components["rapidcheck_rapidcheck"].defines.append("RC_DONT_USE_RTTI")

        if self.options.enable_catch:
            self.cpp_info.components["rapidcheck_catch"].set_property("cmake_target_name", "rapidcheck_catch")
            self.cpp_info.components["rapidcheck_catch"].requires = ["rapidcheck_rapidcheck", "catch2::catch2"]
        if self.options.enable_gmock:
            self.cpp_info.components["rapidcheck_gmock"].set_property("cmake_target_name", "rapidcheck_gmock")
            self.cpp_info.components["rapidcheck_gmock"].requires = ["rapidcheck_rapidcheck", "gtest::gtest"]
        if self.options.enable_gtest:
            self.cpp_info.components["rapidcheck_gtest"].set_property("cmake_target_name", "rapidcheck_gtest")
            self.cpp_info.components["rapidcheck_gtest"].requires = ["rapidcheck_rapidcheck", "gtest::gtest"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["rapidcheck_rapidcheck"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["rapidcheck_rapidcheck"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        if self.options.enable_catch:
            self.cpp_info.components["rapidcheck_catch"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["rapidcheck_catch"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        if self.options.enable_gmock:
            self.cpp_info.components["rapidcheck_gmock"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["rapidcheck_gmock"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        if self.options.enable_gtest:
            self.cpp_info.components["rapidcheck_gtest"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["rapidcheck_gtest"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
