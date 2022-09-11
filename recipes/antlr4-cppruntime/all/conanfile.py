from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os
import textwrap

required_conan_version = ">=1.45.0"


class Antlr4CppRuntimeConan(ConanFile):
    name = "antlr4-cppruntime"
    homepage = "https://github.com/antlr/antlr4/tree/master/runtime/Cpp"
    description = "C++ runtime support for ANTLR (ANother Tool for Language Recognition)"
    topics = ("antlr", "parser", "runtime")
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "pkg_config"
    short_paths = True

    compiler_required_cpp17 = {
            "Visual Studio": "16",
            "gcc": "7",
            "clang": "5",
            "apple-clang": "9.1"
    }


    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

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
        antlr_version = tools.Version(self.version)
        self.requires("utfcpp/3.2.1")
        # As of 4.11, antlr4-cppruntime no longer requires libuuid.
        # Reference: [C++] Remove libuuid dependency (https://github.com/antlr/antlr4/pull/3787)
        if self.settings.os in ("FreeBSD", "Linux") and antlr_version < "4.11":
            self.requires("libuuid/1.0.3")

    def validate(self):
        compiler = self.settings.compiler
        compiler_version = tools.Version(self.settings.compiler.version)
        antlr_version = tools.Version(self.version)

        if str(self.settings.arch).startswith("arm") and antlr_version < "4.11":
            raise ConanInvalidConfiguration("arm architectures are not supported due to libuuid; please upgrade to antlr 4.11 or later.")
            # Need to deal with missing libuuid on Arm.
            # So far ANTLR delivers macOS binary package.

        if compiler == "Visual Studio" and compiler_version < "16":
            raise ConanInvalidConfiguration("library claims C2668 'Ambiguous call to overloaded function'")
            # Compilation of this library on version 15 claims C2668 Error.
            # This could be Bogus error or malformed Antl4 libary.
            # Version 16 compiles this code correctly.

        if antlr_version >= "4.10":
            # Antlr4 for 4.9.3 does not require C++17 - C++11 is enough.
            # for newest version we need C++17 compatible compiler here

            if self.settings.get_safe("compiler.cppstd"):
                tools.check_min_cppstd(self, "17")

            minimum_version = self.compiler_required_cpp17.get(str(self.settings.compiler), False)
            if minimum_version:
                if compiler_version < minimum_version:
                    raise ConanInvalidConfiguration("{} requires C++17, which your compiler does not support.".format(self.name))
            else:
                self.output.warn("{} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name))

        if is_msvc(self) and antlr_version == "4.10":
            raise ConanInvalidConfiguration("{} Antlr4 4.10 version is broken on msvc - Use 4.10.1 or above.".format(self.name))

    def build_requirements(self):
        if self.settings.os in ("FreeBSD", "Linux"):
            self.build_requires("pkgconf/1.7.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ANTLR4_INSTALL"] = True
        cmake.definitions["WITH_LIBCXX"] = self.settings.compiler.get_safe("libcxx") == "libc++"
        cmake.definitions["ANTLR_BUILD_CPP_TESTS"] = False
        if is_msvc(self):
            cmake.definitions["WITH_STATIC_CRT"] = is_msvc_static_runtime(self)
        cmake.definitions["WITH_DEMO"] = False
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        if self.options.shared:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*antlr4-runtime-static.*")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*antlr4-runtime.a")
        else:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.dll")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "antlr4-runtime.lib")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*antlr4-runtime.so*")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*antlr4-runtime.dll*")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*antlr4-runtime.*dylib")
        tools.rmdir(os.path.join(self.package_folder, "share"))

        # FIXME: this also removes lib/cmake/antlr4-generator
        # This cmake config script is needed to provide the cmake function `antlr4_generate`
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

        # TODO: to remove in conan v2 once cmake_find_package* generatores removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"antlr4_shared" if self.options.shared else "antlr4_static": "antlr4-cppruntime::antlr4-cppruntime"}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        tools.save(module_file, content)

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
