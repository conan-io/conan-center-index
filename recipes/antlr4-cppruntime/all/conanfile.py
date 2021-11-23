from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os
import textwrap

required_conan_version = ">=1.33.0"


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
    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def requirements(self):
        self.requires("utfcpp/3.2.1")
        if self.settings.os in ("FreeBSD", "Linux"):
            self.requires("libuuid/1.0.3")

    def validate(self):
        if str(self.settings.arch).startswith("arm"):
            raise ConanInvalidConfiguration(f"arm architectures are not supported")
            # Need to deal with missing libuuid on Arm.
            # So far ANTLR delivers macOS binary package.
        compiler, version = self.settings.compiler, tools.Version(self.settings.compiler.version)
        if compiler == "Visual Studio" and version < "16":
            raise ConanInvalidConfiguration(f"library claims C2668 'Ambiguous call to overloaded function'")
            # Compilation of this library on version 15 claims C2668 Error.
            # This could be Bogus error or malformed Antl4 libary.
            # Version 16 compiles this code correctly.

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ANTLR4_INSTALL"] = True
        cmake.definitions["WITH_LIBCXX"] = self.settings.compiler.get_safe("libcxx") == "libc++"
        if self.settings.compiler == "Visual Studio":
            cmake.definitions["WITH_STATIC_CRT"] = "MT" in self.settings.compiler.runtime
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
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*antlr4-runtime.dylib*")
        tools.rmdir(os.path.join(self.package_folder, "share"))

        # FIXME: this also removes lib/cmake/antlr4-generator
        # This cmake config script is needed to provide the cmake function `antlr4_generate`
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

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
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder, f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        libname = "antlr4-runtime"
        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            libname += "-static"
        self.cpp_info.libs = [libname]
        self.cpp_info.includedirs.append(os.path.join("include", "antlr4-runtime"))
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.builddirs.append(self._module_subfolder)
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines.append("ANTLR4CPP_STATIC")
