from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.scm import Version
from conan.tools.files import copy, get, export_conandata_patches, apply_conandata_patches, save
from conan.tools.layout import cmake_layout
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.53.0"


class YACLibConan(ConanFile):
    name = "yaclib"
    description = "lightweight C++ library for concurrent and parallel task execution"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/YACLib/YACLib"
    license = "MIT"
    topics = ("async", "parallel", "concurrency")
    settings = "os", "arch", "compiler", "build_type"

    _yaclib_flags = {
        "warn": [True, False],
        "coro": [True, False],
        "disable_futex": [True, False],
        "disable_unsafe_futex": [True, False],
        "disable_symmetric_transfer": [True, False],
        "disable_final_suspend_transfer": [True, False],
    }

    options = {
        "fPIC": [True, False],
        **_yaclib_flags,
    }

    default_options = {
        "fPIC": True,
        **{k: False for k in _yaclib_flags},
    }

    @property
    def _min_cppstd(self):
        return 20 if self.options.coro else 17

    @property
    def _compilers_minimum_version(self):
        if self._min_cppstd == 17:
            return {
                "gcc": "7",
                "Visual Studio": "14.20",
                "msvc": "192",
                "clang": "8",
                "apple-clang": "12",
            }
        return {
            "gcc": "12",
            "Visual Studio": "16",
            "msvc": "192",
            "clang": "13",
            "apple-clang": "13",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables['YACLIB_INSTALL'] = True
        if self.settings.compiler.get_safe("cppstd"):
            tc.variables["YACLIB_CXX_STANDARD"] = self.settings.compiler.cppstd

        flags = []
        for flag in self._yaclib_flags:
            if self.options.get_safe(flag):
                flags.append(flag.upper())
        if flags:
            tc.variables["YACLIB_FLAGS"] = ";".join(flags)

        tc.generate()

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

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
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"yaclib": "yaclib::yaclib"}
        )

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "yaclib")
        self.cpp_info.set_property("cmake_target_name", "yaclib")
        self.cpp_info.set_property("pkg_config_name", "yaclib")
        self.cpp_info.libs = ["yaclib"]
        if self.options.get_safe("coro"):
            if self.settings.compiler.libcxx == "libstdc++11":
                self.cpp_info.cxxflags.append("-fcoroutines")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "yaclib"
        self.cpp_info.names["cmake_find_package_multi"] = "yaclib"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "yaclib"
