from conan import ConanFile
from conan.tools.files import copy, get, apply_conandata_patches, replace_in_file, rmdir, save
from conan.tools.scm import Version
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.errors import ConanInvalidConfiguration
import os
import textwrap


required_conan_version = ">=1.51.3"


class SQLiteCppConan(ConanFile):
    name = "sqlitecpp"
    description = "SQLiteCpp is a smart and easy to use C++ sqlite3 wrapper"
    topics = ("sqlite", "sqlite3", "data-base")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/SRombauts/SQLiteCpp"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "stack_protection": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "stack_protection": True,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def requirements(self):
        self.requires("sqlite3/3.39.2")

    def validate(self):
        if Version(self.version) >= "3.0.0" and self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("SQLiteCpp can not be built as shared lib on Windows")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)
        if self.settings.compiler == "clang" and \
           Version(self.settings.compiler.version) < "6.0" and \
                 self.settings.compiler.libcxx == "libc++" and \
                 Version(self.version) < "3":
            replace_in_file(self,
                os.path.join(self._source_subfolder, "include", "SQLiteCpp", "Utils.h"),
                "const nullptr_t nullptr = {};",
                "")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SQLITECPP_INTERNAL_SQLITE"] = False
        tc.variables["SQLITECPP_RUN_CPPLINT"] = False
        tc.variables["SQLITECPP_RUN_CPPCHECK"] = False
        tc.variables["SQLITECPP_RUN_DOXYGEN"] = False
        tc.variables["SQLITECPP_BUILD_EXAMPLES"] = False
        tc.variables["SQLITECPP_BUILD_TESTS"] = False
        tc.variables["SQLITECPP_USE_STACK_PROTECTION"] = self.options.stack_protection
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            self,
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"SQLiteCpp": "SQLiteCpp::SQLiteCpp"}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(conanfile, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        save(conanfile, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SQLiteCpp")
        self.cpp_info.set_property("cmake_target_name", "SQLiteCpp")
        self.cpp_info.libs = ["SQLiteCpp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "dl", "m"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "SQLiteCpp"
        self.cpp_info.names["cmake_find_package_multi"] = "SQLiteCpp"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
