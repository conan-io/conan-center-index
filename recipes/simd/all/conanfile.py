import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir, replace_in_file, collect_libs
from conan.tools.microsoft import is_msvc, MSBuild, MSBuildToolchain, is_msvc_static_runtime, msvs_toolset

required_conan_version = ">=1.59.0"


class SimdConan(ConanFile):
    name = "simd"
    description = "C++ image processing and machine learning library with SIMD"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ermig1979/Simd"
    topics = ("sse", "avx", "avx-512", "amx", "vmx", "vsx", "neon")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    @property
    def _min_cppstd(self):
        return 11

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        if self.settings.os == "Windows" and self.settings.arch not in ["x86", "x86_64"]:
            raise ConanInvalidConfiguration("Windows only supports x86/x64 architectures.")
        if is_msvc(self) and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration("ARM64 building with MSVC is not supported.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.generate()
        else:
            tc = CMakeToolchain(self)
            tc.variables["SIMD_TEST"] = False
            tc.variables["SIMD_SHARED"] = self.options.shared
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
            tc.generate()

    @property
    def vs_proj_folder(self):
        """Return the vsXXXX/ folder given the MSVC compiler version"""
        toolset = msvs_toolset(self)
        # By default, v2022 folder
        return {"v140": "vs2015",
                "v141": "vs2017",
                "v142": "vs2019"}.get(toolset, "vs2022")

    def _patch_sources(self):
        if is_msvc(self):
            if not self.options.shared:
                replace_in_file(self, os.path.join(self.source_folder, "src", "Simd", "SimdConfig.h"), "//#define SIMD_STATIC", "#define SIMD_STATIC")
                replace_in_file(self, os.path.join(self.source_folder, "prj", self.vs_proj_folder, "Simd.vcxproj"),
                                "<ConfigurationType>DynamicLibrary</ConfigurationType>",
                                "<ConfigurationType>StaticLibrary</ConfigurationType>")
                for prj in ("AmxBf16", "Avx2", "Avx512bw", "Avx512vnni", "Base", "Neon", "Simd", "Sse41"):
                    replace_in_file(self, os.path.join(self.source_folder, "prj", self.vs_proj_folder, f"{prj}.vcxproj"),
                                    "    </ClCompile>",
                                    "      <DebugInformationFormat>OldStyle</DebugInformationFormat>\n    </ClCompile>")

            if not is_msvc_static_runtime(self):
                for prj in ("AmxBf16", "Avx2", "Avx512bw", "Avx512vnni", "Base", "Neon", "Simd", "Sse41"):
                    replace_in_file(self, os.path.join(self.source_folder, "prj", self.vs_proj_folder, f"{prj}.vcxproj"),
                                    "    </ClCompile>",
                                    "      <RuntimeLibrary Condition=\"'$(Configuration)'=='Debug'\">MultiThreadedDebugDLL</RuntimeLibrary>\n"
                                    "      <RuntimeLibrary Condition=\"'$(Configuration)'=='Release'\">MultiThreadedDLL</RuntimeLibrary>\n"
                                    "    </ClCompile>")

    def build(self):
        self._patch_sources()
        if is_msvc(self):
            msbuild = MSBuild(self)
            msbuild.build(os.path.join(self.source_folder, "prj", self.vs_proj_folder, "Simd.vcxproj"))
        else:
            cmake = CMake(self)
            cmake.configure(build_script_folder=os.path.join(self.source_folder, "prj", "cmake"))
            cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if is_msvc(self):
            copy(self, pattern="*.h*", dst=os.path.join(self.package_folder, "include", "Simd"), src=os.path.join(self.source_folder, "src", "Simd"), keep_path=True)
            copy(self, pattern="*.lib", dst=os.path.join(self.package_folder, "lib"), src=self.source_folder, keep_path=False)
            copy(self, pattern="*.dll", dst=os.path.join(self.package_folder, "bin"), src=self.source_folder, keep_path=False)
        else:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.set_property("cmake_file_name", "Simd")
        self.cpp_info.set_property("cmake_target_name", "Simd::Simd")
        if not self.options.shared and is_msvc(self):
            self.cpp_info.defines.append("SIMD_STATIC")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "m"])
