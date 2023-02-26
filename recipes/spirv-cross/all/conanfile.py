from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import stdcpp_library
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, save
import os
import textwrap

required_conan_version = ">=1.54.0"


class SpirvCrossConan(ConanFile):
    name = "spirv-cross"
    description = "SPIRV-Cross is a practical tool and library for performing " \
                  "reflection on SPIR-V and disassembling SPIR-V back to high level languages."
    license = "Apache-2.0"
    topics = ("reflection", "disassembler", "spirv", "spir-v", "glsl", "hlsl")
    homepage = "https://github.com/KhronosGroup/SPIRV-Cross"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_executable": [True, False],
        "exceptions": [True, False],
        "glsl": [True, False],
        "hlsl": [True, False],
        "msl": [True, False],
        "cpp": [True, False],
        "reflect": [True, False],
        "c_api": [True, False],
        "util": [True, False],
        "namespace": ["ANY"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_executable": True,
        "exceptions": True,
        "glsl": True,
        "hlsl": True,
        "msl": True,
        "cpp": True,
        "reflect": True,
        "c_api": True,
        "util": True,
        "namespace": "spirv_cross",
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
            # these options don't contribute to shared binary
            del self.options.c_api
            del self.options.util

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if not self.options.glsl and \
           (self.options.hlsl or self.options.msl or self.options.cpp or self.options.reflect):
            raise ConanInvalidConfiguration("hlsl, msl, cpp and reflect require glsl enabled")

        if self.options.build_executable and \
           not (self.options.glsl and self.options.hlsl and self.options.msl and
                self.options.cpp and self.options.reflect and self.options.get_safe("util", True)):
            raise ConanInvalidConfiguration("executable can't be built without glsl, hlsl, msl, cpp, reflect and util")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SPIRV_CROSS_EXCEPTIONS_TO_ASSERTIONS"] = not self.options.exceptions
        tc.variables["SPIRV_CROSS_SHARED"] = self.options.shared
        tc.variables["SPIRV_CROSS_STATIC"] = not self.options.shared or self.options.build_executable
        tc.variables["SPIRV_CROSS_CLI"] = self.options.build_executable
        tc.variables["SPIRV_CROSS_ENABLE_TESTS"] = False
        tc.variables["SPIRV_CROSS_ENABLE_GLSL"] = self.options.glsl
        tc.variables["SPIRV_CROSS_ENABLE_HLSL"] = self.options.hlsl
        tc.variables["SPIRV_CROSS_ENABLE_MSL"] = self.options.msl
        tc.variables["SPIRV_CROSS_ENABLE_CPP"] = self.options.cpp
        tc.variables["SPIRV_CROSS_ENABLE_REFLECT"] = self.options.reflect
        tc.variables["SPIRV_CROSS_ENABLE_C_API"] = self.options.get_safe("c_api", True)
        tc.variables["SPIRV_CROSS_ENABLE_UTIL"] = self.options.get_safe("util", False) or self.options.build_executable
        tc.variables["SPIRV_CROSS_SKIP_INSTALL"] = False
        tc.variables["SPIRV_CROSS_FORCE_PIC"] = self.options.get_safe("fPIC", True)
        tc.variables["SPIRV_CROSS_NAMESPACE_OVERRIDE"] = self.options.namespace
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.ilk", os.path.join(self.package_folder, "bin"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        if self.options.shared and self.options.build_executable:
            for static_lib in [
                "spirv-cross-core", "spirv-cross-glsl", "spirv-cross-hlsl", "spirv-cross-msl",
                "spirv-cross-cpp", "spirv-cross-reflect", "spirv-cross-c", "spirv-cross-util",
            ]:
                rm(self, f"*{static_lib}.*", os.path.join(self.package_folder, "lib"))

        # TODO: to remove in conan v2 once legacy generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {target: f"spirv-cross::{target}" for target in self._spirv_cross_components.keys()},
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

    @property
    def _spirv_cross_components(self):
        components = {}
        if self.options.shared:
            components.update({"spirv-cross-c-shared": []})
        else:
            components.update({"spirv-cross-core": []})
            if self.options.glsl:
                components.update({"spirv-cross-glsl": ["spirv-cross-core"]})
                if self.options.hlsl:
                    components.update({"spirv-cross-hlsl": ["spirv-cross-glsl"]})
                if self.options.msl:
                    components.update({"spirv-cross-msl": ["spirv-cross-glsl"]})
                if self.options.cpp:
                    components.update({"spirv-cross-cpp": ["spirv-cross-glsl"]})
                if self.options.reflect:
                    components.update({"spirv-cross-reflect": []})
            if self.options.c_api:
                c_api_requires = []
                if self.options.glsl:
                    c_api_requires.append("spirv-cross-glsl")
                    if self.options.hlsl:
                        c_api_requires.append("spirv-cross-hlsl")
                    if self.options.msl:
                        c_api_requires.append("spirv-cross-msl")
                    if self.options.cpp:
                        c_api_requires.append("spirv-cross-cpp")
                    if self.options.reflect:
                        c_api_requires.append("spirv-cross-reflect")
                components.update({"spirv-cross-c": c_api_requires})
            if self.options.util:
                components.update({"spirv-cross-util": ["spirv-cross-core"]})
        return components

    def package_info(self):
        # FIXME: we should provide one CMake config file per target (waiting for an implementation of https://github.com/conan-io/conan/issues/9000)
        def _register_component(target_lib, requires):
            self.cpp_info.components[target_lib].set_property("cmake_target_name", target_lib)
            if self.options.shared:
                self.cpp_info.components[target_lib].set_property("pkg_config_name", target_lib)
            prefix = "d" if self.settings.os == "Windows" and self.settings.build_type == "Debug" else ""
            self.cpp_info.components[target_lib].libs = [f"{target_lib}{prefix}"]
            self.cpp_info.components[target_lib].includedirs.append(os.path.join("include", "spirv_cross"))
            self.cpp_info.components[target_lib].defines.append(f"SPIRV_CROSS_NAMESPACE_OVERRIDE={self.options.namespace}")
            self.cpp_info.components[target_lib].requires = requires
            if self.settings.os in ["Linux", "FreeBSD"] and self.options.glsl:
                self.cpp_info.components[target_lib].system_libs.append("m")
            if not self.options.shared and self.options.c_api:
                libcxx = stdcpp_library(self)
                if libcxx:
                    self.cpp_info.components[target_lib].system_libs.append(libcxx)

            # TODO: to remove in conan v2 once legacy generators removed
            self.cpp_info.components[target_lib].names["cmake_find_package"] = target_lib
            self.cpp_info.components[target_lib].names["cmake_find_package_multi"] = target_lib
            self.cpp_info.components[target_lib].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components[target_lib].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

        for target_lib, requires in self._spirv_cross_components.items():
            _register_component(target_lib, requires)

        # TODO: to remove in conan v2 once legacy generators removed
        if self.options.build_executable:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
