import os
import re

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version

required_conan_version = ">=1.54.0"


class GlslangConan(ConanFile):
    name = "glslang"
    description = "Khronos-reference front end for GLSL/ESSL, partial front " \
                  "end for HLSL, and a SPIR-V generator."
    license = "DocumentRef-LICENSE.txt:LicenseRef-glslang"
    topics = ("glsl", "hlsl", "spirv", "spir-v", "validation", "translation")
    homepage = "https://github.com/KhronosGroup/glslang"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_executables": [True, False],
        "spv_remapper": [True, False],
        "hlsl": [True, False],
        "enable_optimizer": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_executables": True,
        "spv_remapper": True,
        "hlsl": True,
        "enable_optimizer": True,
    }

    short_paths = True

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.enable_optimizer:
            self.requires(f"spirv-tools/{self.version}")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

        # see https://github.com/KhronosGroup/glslang/issues/2283
        if self.options.shared:
            if self.settings.os == "Windows":
                raise ConanInvalidConfiguration(f"{self.ref} shared library build is broken on {self.settings.os}")

        if self.options.enable_optimizer and self.dependencies["spirv-tools"].options.shared:
            raise ConanInvalidConfiguration(
                f"{self.ref} with enable_optimizer requires static spirv-tools, "
                "because SPIRV-Tools-opt is not built if shared"
            )

    def build_requirements(self):
        if Version(self.version) >= "1.3.261":
            self.tool_requires("cmake/[>=3.17.2 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()

        tc = CMakeToolchain(self)
        tc.variables["BUILD_EXTERNAL"] = False
        tc.variables["SKIP_GLSLANG_INSTALL"] = False
        tc.variables["ENABLE_SPVREMAPPER"] = self.options.spv_remapper
        tc.variables["ENABLE_GLSLANG_BINARIES"] = self.options.build_executables
        tc.variables["ENABLE_GLSLANG_JS"] = False
        tc.variables["ENABLE_GLSLANG_WEBMIN"] = False
        tc.variables["ENABLE_GLSLANG_WEBMIN_DEVEL"] = False
        tc.variables["ENABLE_EMSCRIPTEN_SINGLE_FILE"] = False
        tc.variables["ENABLE_EMSCRIPTEN_ENVIRONMENT_NODE"] = False
        tc.variables["ENABLE_HLSL"] = self.options.hlsl
        tc.variables["ENABLE_RTTI"] = True
        tc.variables["ENABLE_OPT"] = self.options.enable_optimizer
        if self.options.enable_optimizer:
            tc.variables["spirv-tools_SOURCE_DIR"] = self.dependencies["spirv-tools"].package_folder.replace("\\", "/")
        tc.variables["ENABLE_PCH"] = False
        tc.variables["ENABLE_CTEST"] = False
        tc.variables["USE_CCACHE"] = False
        tc.variables["OVERRIDE_MSVCCRT"] = False
        tc.variables["CMAKE_MACOSX_BUNDLE"] = False
        # Generate a relocatable shared lib on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        # glslang builds intermediate static libs, but Conan does not set -fPIC for shared builds
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        for cmake_file in sorted(self.source_path.rglob("CMakeLists.txt")):
            content = cmake_file.read_text(encoding="utf8")
            if "POSITION_INDEPENDENT_CODE ON" in content:
                content = re.sub(r"set_property\(TARGET \S+ PROPERTY POSITION_INDEPENDENT_CODE ON\)\n", "", content)
                content = content.replace("POSITION_INDEPENDENT_CODE ON", "")
                cmake_file.write_text(content, encoding="utf8")
                self.output.info(f"Patched fPIC handling in {cmake_file.relative_to(self.source_path)}")
            if "POSITION_INDEPENDENT_CODE" in content:
                raise ConanException(f"POSITION_INDEPENDENT_CODE found in {cmake_file}, please update the recipe")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "glslang")
        self.cpp_info.set_property("cmake_target_name", "glslang::_glslang-do-not-use") # because glslang-core target is glslang::glslang

        lib_suffix = "d" if self.settings.os == "Windows" and self.settings.build_type == "Debug" else ""

        has_machineindependent = not self.options.shared
        has_genericcodegen = not self.options.shared
        has_osdependent = not self.options.shared
        has_oglcompiler = not self.options.shared

        # glslang
        self.cpp_info.components["glslang-core"].set_property("cmake_target_name", "glslang::glslang")
        self.cpp_info.components["glslang-core"].names["cmake_find_package"] = "glslang"
        self.cpp_info.components["glslang-core"].names["cmake_find_package_multi"] = "glslang"
        self.cpp_info.components["glslang-core"].libs = [f"glslang{lib_suffix}"]
        if self.options.shared:
            self.cpp_info.components["glslang-core"].defines.append("GLSLANG_IS_SHARED_LIBRARY")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["glslang-core"].system_libs.extend(["m", "pthread"])
        if has_machineindependent:
            self.cpp_info.components["glslang-core"].requires.append("machineindependent")
        if has_genericcodegen:
            self.cpp_info.components["glslang-core"].requires.append("genericcodegen")
        if has_osdependent:
            self.cpp_info.components["glslang-core"].requires.append("osdependent")
        if has_oglcompiler:
            self.cpp_info.components["glslang-core"].requires.append("oglcompiler")
        if self.options.hlsl:
            self.cpp_info.components["glslang-core"].defines.append("ENABLE_HLSL")
            self.cpp_info.components["glslang-core"].requires.append("hlsl")

        if has_machineindependent:
            # MachineIndependent
            self.cpp_info.components["machineindependent"].set_property("cmake_target_name", "glslang::MachineIndependent")
            self.cpp_info.components["machineindependent"].names["cmake_find_package"] = "MachineIndependent"
            self.cpp_info.components["machineindependent"].names["cmake_find_package_multi"] = "MachineIndependent"
            self.cpp_info.components["machineindependent"].libs = [f"MachineIndependent{lib_suffix}"]
            if has_genericcodegen:
                self.cpp_info.components["machineindependent"].requires.append("genericcodegen")
            if has_osdependent:
                self.cpp_info.components["machineindependent"].requires.append("osdependent")
            if has_oglcompiler:
                self.cpp_info.components["machineindependent"].requires.append("oglcompiler")

        if has_genericcodegen:
            # GenericCodeGen
            self.cpp_info.components["genericcodegen"].set_property("cmake_target_name", "glslang::GenericCodeGen")
            self.cpp_info.components["genericcodegen"].names["cmake_find_package"] = "GenericCodeGen"
            self.cpp_info.components["genericcodegen"].names["cmake_find_package_multi"] = "GenericCodeGen"
            self.cpp_info.components["genericcodegen"].libs = [f"GenericCodeGen{lib_suffix}"]

        if has_osdependent:
            # OSDependent
            self.cpp_info.components["osdependent"].set_property("cmake_target_name", "glslang::OSDependent")
            self.cpp_info.components["osdependent"].names["cmake_find_package"] = "OSDependent"
            self.cpp_info.components["osdependent"].names["cmake_find_package_multi"] = "OSDependent"
            self.cpp_info.components["osdependent"].libs = [f"OSDependent{lib_suffix}"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["osdependent"].system_libs.append("pthread")

        if has_oglcompiler:
            # OGLCompiler
            self.cpp_info.components["oglcompiler"].set_property("cmake_target_name", "glslang::OGLCompiler")
            self.cpp_info.components["oglcompiler"].names["cmake_find_package"] = "OGLCompiler"
            self.cpp_info.components["oglcompiler"].names["cmake_find_package_multi"] = "OGLCompiler"
            self.cpp_info.components["oglcompiler"].libs = [f"OGLCompiler{lib_suffix}"]

        # SPIRV
        self.cpp_info.components["spirv"].set_property("cmake_target_name", "glslang::SPIRV")
        self.cpp_info.components["spirv"].names["cmake_find_package"] = "SPIRV"
        self.cpp_info.components["spirv"].names["cmake_find_package_multi"] = "SPIRV"
        self.cpp_info.components["spirv"].libs = [f"SPIRV{lib_suffix}"]
        self.cpp_info.components["spirv"].requires = ["glslang-core"]
        if self.options.enable_optimizer:
            self.cpp_info.components["spirv"].requires.append("spirv-tools::spirv-tools-opt")
            self.cpp_info.components["spirv"].defines.append("ENABLE_OPT")

        # HLSL
        if self.options.hlsl:
            self.cpp_info.components["hlsl"].set_property("cmake_target_name", "glslang::HLSL")
            self.cpp_info.components["hlsl"].names["cmake_find_package"] = "HLSL"
            self.cpp_info.components["hlsl"].names["cmake_find_package_multi"] = "HLSL"
            self.cpp_info.components["hlsl"].libs = [f"HLSL{lib_suffix}"]

        # SPVRemapper
        if self.options.spv_remapper:
            self.cpp_info.components["spvremapper"].set_property("cmake_target_name", "glslang::SPVRemapper")
            self.cpp_info.components["spvremapper"].names["cmake_find_package"] = "SPVRemapper"
            self.cpp_info.components["spvremapper"].names["cmake_find_package_multi"] = "SPVRemapper"
            self.cpp_info.components["spvremapper"].libs = [f"SPVRemapper{lib_suffix}"]

        if self.options.build_executables:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

        if Version(self.version) >= "1.3.243":
            self.cpp_info.components["glslang-default-resource-limits"].set_property("cmake_target_name", "glslang::glslang-default-resource-limits")
            self.cpp_info.components["glslang-default-resource-limits"].names["cmake_find_package"] = "glslang-default-resource-limits"
            self.cpp_info.components["glslang-default-resource-limits"].names["cmake_find_package_multi"] = "glslang-default-resource-limits"
            self.cpp_info.components["glslang-default-resource-limits"].libs = [f"glslang-default-resource-limits{lib_suffix}"]
