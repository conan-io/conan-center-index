from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, save
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
from os.path import join
import textwrap

required_conan_version = ">=1.53.0"


class RapidcheckConan(ConanFile):
    name = "rapidcheck"
    description = "QuickCheck clone for C++ with the goal of being simple to use with as little boilerplate as possible"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/emil-e/rapidcheck"
    license = "BSD-2-Clause"
    topics = ("quickcheck", "testing", "property-testing")
    package_type = "library"
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

    @property
    def _min_cppstd(self):
        return 11

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.enable_catch:
            self.requires("catch2/2.13.10")
        if self.options.enable_gmock or self.options.enable_gtest:
            self.requires("gtest/1.12.1")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Visual Studio and msvc.")
        if self.options.enable_gmock and not self.dependencies["gtest"].options.build_gmock:
            raise ConanInvalidConfiguration("The option `rapidcheck:enable_gmock` requires `gtest/*:build_gmock=True`")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["RC_ENABLE_RTTI"] = self.options.enable_rtti
        tc.variables["RC_ENABLE_TESTS"] = False
        tc.variables["RC_ENABLE_EXAMPLES"] = False
        tc.variables["RC_ENABLE_CATCH"] = self.options.enable_catch
        tc.variables["RC_ENABLE_GMOCK"] = self.options.enable_gmock
        tc.variables["RC_ENABLE_GTEST"] = self.options.enable_gtest
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE*", dst=join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, join(self.package_folder, "share"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            join(self.package_folder, self._module_file_rel_path),
            {
                "rapidcheck": "rapidcheck::rapidcheck_rapidcheck",
                "rapidcheck_catch":"rapidcheck::rapidcheck_catch",
                "rapidcheck_gmock": "rapidcheck::rapidcheck_gmock",
                "rapidcheck_gtest": "rapidcheck::rapidcheck_gtest",
            }
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "rapidcheck")

        self.cpp_info.components["rapidcheck_rapidcheck"].set_property("cmake_target_name", "rapidcheck")
        self.cpp_info.components["rapidcheck_rapidcheck"].libs = ["rapidcheck"]
        version = str(self.version)[4:]
        if Version(version) < "20201218":
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

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

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
