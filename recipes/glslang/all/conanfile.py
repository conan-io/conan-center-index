from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class GlslangConan(ConanFile):
    name = "glslang"
    description = "Khronos-reference front end for GLSL/ESSL, partial front " \
                  "end for HLSL, and a SPIR-V generator."
    license = ["BSD-3-Clause", "NVIDIA"]
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
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    @property
    def _get_compatible_spirv_tools_version(self):
        return {
            "11.7.0": "2021.4",
            "11.6.0": "2021.3",
            "11.5.0": "2021.2",
            "8.13.3559": "2020.5",
        }.get(str(self.version), self.version)

    def requirements(self):
        if self.options.enable_optimizer:
            self.requires(f"spirv-tools/{self._get_compatible_spirv_tools_version}")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

        # see https://github.com/KhronosGroup/glslang/issues/2283
        glslang_version = Version(self.version)
        if (self.options.shared and
            (self.settings.os == "Windows" or \
             (glslang_version >= "7.0.0" and glslang_version < "11.0.0" and is_apple_os(self)))
           ):
            raise ConanInvalidConfiguration(f"{self.ref} shared library build is broken on {self.settings.os}")

        if self.options.enable_optimizer and self.dependencies["spirv-tools"].options.shared:
            raise ConanInvalidConfiguration(
                f"{self.ref} with enable_optimizer requires static spirv-tools, "
                "because SPIRV-Tools-opt is not built if shared"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_EXTERNAL"] = False
        tc.variables["SKIP_GLSLANG_INSTALL"] = False
        tc.variables["ENABLE_SPVREMAPPER"] = self.options.spv_remapper
        tc.variables["ENABLE_GLSLANG_BINARIES"] = self.options.build_executables
        glslang_version = Version(self.version)
        if glslang_version < "7.0.0" or glslang_version >= "8.13.3743":
            tc.variables["ENABLE_GLSLANG_JS"] = False
            tc.variables["ENABLE_GLSLANG_WEBMIN"] = False
            tc.variables["ENABLE_GLSLANG_WEBMIN_DEVEL"] = False
        else:
            tc.variables["ENABLE_GLSLANG_WEB"] = False
            tc.variables["ENABLE_GLSLANG_WEB_DEVEL"] = False
        tc.variables["ENABLE_EMSCRIPTEN_SINGLE_FILE"] = False
        tc.variables["ENABLE_EMSCRIPTEN_ENVIRONMENT_NODE"] = False
        tc.variables["ENABLE_HLSL"] = self.options.hlsl
        if glslang_version < "7.0.0" or glslang_version >= "8.13.3743":
            tc.variables["ENABLE_RTTI"] = True
        tc.variables["ENABLE_OPT"] = self.options.enable_optimizer
        if self.options.enable_optimizer:
            tc.variables["spirv-tools_SOURCE_DIR"] = self.dependencies["spirv-tools"].package_folder.replace("\\", "/")
        tc.variables["ENABLE_PCH"] = False
        tc.variables["ENABLE_CTEST"] = False
        tc.variables["USE_CCACHE"] = False
        if (glslang_version < "7.0.0" or glslang_version >= "11.6.0") and self.settings.os == "Windows":
            tc.variables["OVERRIDE_MSVCCRT"] = False
        if is_apple_os(self):
            tc.variables["CMAKE_MACOSX_BUNDLE"] = False
        if glslang_version < "1.3.231" or glslang_version >= "7.0.0":
            # Generate a relocatable shared lib on Macos
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Do not force PIC if static (but keep it if shared, because OGLCompiler, OSDependent,
        # GenericCodeGen and MachineIndependent are still static and linked to glslang shared)
        if not self.options.shared:
            cmake_files_to_fix = [
                {"target": "OGLCompiler", "relpath": os.path.join("OGLCompilersDLL", "CMakeLists.txt")},
                {"target": "SPIRV"      , "relpath": os.path.join("SPIRV", "CMakeLists.txt")},
                {"target": "SPVRemapper", "relpath": os.path.join("SPIRV", "CMakeLists.txt")},
                {"target": "OSDependent", "relpath": os.path.join("glslang", "OSDependent", "Unix","CMakeLists.txt")},
                {"target": "OSDependent", "relpath": os.path.join("glslang", "OSDependent", "Windows","CMakeLists.txt")},
                {"target": "HLSL"       , "relpath": os.path.join("hlsl", "CMakeLists.txt")},
            ]
            glslang_version = Version(self.version)
            if glslang_version >= "7.0.0" and glslang_version < "11.0.0":
                cmake_files_to_fix.append({"target": "glslang", "relpath": os.path.join("glslang", "CMakeLists.txt")})
            else:
                cmake_files_to_fix.append({"target": "glslang-default-resource-limits", "relpath": os.path.join("StandAlone" , "CMakeLists.txt")})
                cmake_files_to_fix.append({"target": "MachineIndependent", "relpath": os.path.join("glslang", "CMakeLists.txt")})
                cmake_files_to_fix.append({"target": "GenericCodeGen", "relpath": os.path.join("glslang", "CMakeLists.txt")})
            for cmake_file in cmake_files_to_fix:
                replace_in_file(self, os.path.join(self.source_folder, cmake_file["relpath"]),
                                      "set_property(TARGET {} PROPERTY POSITION_INDEPENDENT_CODE ON)".format(cmake_file["target"]),
                                      "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "glslang")
        self.cpp_info.set_property("cmake_target_name", "glslang::glslang-do-not-use") # because glslang-core target is glslang::glslang

        lib_suffix = "d" if self.settings.os == "Windows" and self.settings.build_type == "Debug" else ""

        glslang_version = Version(self.version)
        has_machineindependent = (glslang_version < "7.0.0" or glslang_version >= "11.0.0") and not self.options.shared
        has_genericcodegen = (glslang_version < "7.0.0" or glslang_version >= "11.0.0") and not self.options.shared
        has_osdependent = glslang_version < "1.3.231" or glslang_version >= "7.0.0" or not self.options.shared
        has_oglcompiler = glslang_version < "1.3.231" or glslang_version >= "7.0.0" or not self.options.shared

        # glslang
        self.cpp_info.components["glslang-core"].set_property("cmake_target_name", "glslang::glslang")
        self.cpp_info.components["glslang-core"].names["cmake_find_package"] = "glslang"
        self.cpp_info.components["glslang-core"].names["cmake_find_package_multi"] = "glslang"
        self.cpp_info.components["glslang-core"].libs = [f"glslang{lib_suffix}"]
        if (glslang_version < "7.0.0" or glslang_version >= "11.0.0") and self.options.shared:
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
