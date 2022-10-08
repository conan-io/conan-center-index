from conan import ConanFile
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, check_min_vs
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import export_conandata_patches, apply_conandata_patches, get, copy, rm, rmdir, save
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.52.0"


class Antlr4CppRuntimeConan(ConanFile):
    name = "antlr4-cppruntime"
    homepage = "https://github.com/antlr/antlr4/tree/master/runtime/Cpp"
    description = "C++ runtime support for ANTLR (ANother Tool for Language Recognition)"
    topics = ("antlr", "parser", "runtime")
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    short_paths = True

    @property
    def _minimum_cpp_standard(self):
        # Antlr 4.9.3 requires C++11 while newer versions require C++17
        return 17 if Version(self.version) >= "4.10" else 11

    @property
    def _minimum_compiler_versions_cpp17(self):
        return {
            "Visual Studio": "16",
            "msvc": "1923",
            "gcc": "7",
            "clang": "5",
            "apple-clang": "9.1"
        }

    def _check_minimum_compiler_version_cpp17(self):
        compiler = self.info.settings.compiler
        min_compiler_version = self._minimum_compiler_versions_cpp17.get(str(compiler), False)
        if min_compiler_version and Version(compiler.version) < min_compiler_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++17, which your compiler does not support.")

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # As of 4.11, antlr4-cppruntime no longer requires libuuid.
        # Reference: [C++] Remove libuuid dependency (https://github.com/antlr/antlr4/pull/3787)
        # Note that the above PR points that libuuid can be removed from 4.9.3, 4.10 and 4.10.1 as well.
        # We have patched the CMakeLists.txt to drop the dependency on libuuid from aforementioned antlr versions.
        self.requires("utfcpp/3.2.1")

    def validate(self):
        # Compilation of this library on version 15 claims C2668 Error.
        # This could be Bogus error or malformed Antlr4 library.
        # Guard: The minimum MSVC version is 16 or 1920
        check_min_vs(self, "192")

        # Check the compiler
        min_cppstd = self._minimum_cpp_standard
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, min_cppstd)
        if min_cppstd == 17:
            self._check_minimum_compiler_version_cpp17()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ANTLR4_INSTALL"] = True
        tc.variables["WITH_LIBCXX"] = self.settings.compiler.get_safe("libcxx") == "libc++"
        tc.variables["ANTLR_BUILD_CPP_TESTS"] = False
        if is_msvc(self):
            tc.cache_variables["WITH_STATIC_CRT"] = is_msvc_static_runtime(self)
        tc.variables["WITH_DEMO"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder="runtime/Cpp")
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=os.path.join(self.source_folder), dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        if self.options.shared:
            rm(self, "*antlr4-runtime-static.*", os.path.join(self.package_folder, "lib"))
            rm(self, "*antlr4-runtime.a", os.path.join(self.package_folder, "lib"))
        else:
            rm(self, "*.dll", os.path.join(self.package_folder, "bin"))
            rm(self, "antlr4-runtime.lib", os.path.join(self.package_folder, "lib"))
            rm(self, "*antlr4-runtime.so*", os.path.join(self.package_folder, "lib"))
            rm(self, "*antlr4-runtime.dll*", os.path.join(self.package_folder, "lib"))
            rm(self, "*antlr4-runtime.*dylib", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        # FIXME: this also removes lib/cmake/antlr4-generator
        # This cmake config script is needed to provide the cmake function `antlr4_generate`
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        # TODO: to remove in conan v2 once cmake_find_package* generatores removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"antlr4_shared" if self.options.shared else "antlr4_static": "antlr4-cppruntime::antlr4-cppruntime"}
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "antlr4-runtime")
        self.cpp_info.set_property("cmake_target_name", "antlr4_shared" if self.options.shared else "antlr4_static")
        libname = "antlr4-runtime"
        if is_msvc(self) and not self.options.shared:
            libname += "-static"
        self.cpp_info.libs = [libname]
        self.cpp_info.includedirs.append(os.path.join("include", "antlr4-runtime"))
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines.append("ANTLR4CPP_STATIC")
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread"]

        # TODO: to remove in conan v2 once cmake_find_package* generatores removed
        self.cpp_info.filenames["cmake_find_package"] = "antlr4-runtime"
        self.cpp_info.filenames["cmake_find_package_multi"] = "antlr4-runtime"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
