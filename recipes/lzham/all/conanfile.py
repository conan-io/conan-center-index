import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    replace_in_file,
    rmdir
)
from conan.tools.microsoft import (
    MSBuild, MSBuildDeps, MSBuildToolchain, VCVars, is_msvc, vs_layout
)

required_conan_version = ">=1.52.0"

SLN_FILE = "lzham.sln"


class PackageConan(ConanFile):
    name = "lzham"

    description = (
        "Compression algorithm similar compression ratio and faster "
        "decompression than LZMA."
    )

    license = "LicenseRef-LICENSE"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/richgel999/lzham_codec"
    topics = ("compression", "lz-compression")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        if self.settings.os == "Windows" and self.settings.arch not in ["x86", "x86_64"]:
            raise ConanInvalidConfiguration("On Windows, only x86 and x86_64 are supported")
        
    def _msvc_libs(self, targets=False):
        arch = "x86" if self.settings.arch == "x86" else "x64"
        suffix = f"{arch}D" if self.settings.build_type == "Debug" else arch
        if self.options.shared == True:
            if targets:
                 # Note: this causes its dependencies to be built too
                return ['lzhamdll']
            
            files = [f"lzham_{suffix}.dll", f"lzham_{suffix}.lib"]
        else:
            libs = ['lzhamcomp', 'lzhamdecomp', 'lzhamlib']
            if targets:
                return libs
            
            files = [f"{lib}_{suffix}.lib" for lib in libs]
            
        return files

    def layout(self):
        if is_msvc(self):
            vs_layout(self)
        else:
            cmake_layout(self, src_folder="src")

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            destination=self.source_folder,
            strip_root=True
        )

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.generate()
            tc = MSBuildDeps(self)
            tc.generate()
            tc = VCVars(self)
            tc.generate()
        else:
            tc = CMakeToolchain(self)

            # Honor BUILD_SHARED_LIBS from conan_toolchain (see
            # https://github.com/conan-io/conan/issues/11840)
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"

            # Build relocatable shared libraries on Apple OSs
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
            tc.generate()

    def build(self):
        apply_conandata_patches(self)
        for project in ['lzhamcomp', 'lzhamdecomp', 'lzhamdll', 'lzhamlib']:
            filename = 'lzham' if project == 'lzhamdll' else project
            vcxproj_file = os.path.join(self.source_folder, project, f"{filename}.vcxproj")
            # Avoid errors when the toolset on the consumer side is not exactly the same version
            replace_in_file(self, vcxproj_file, "WholeProgramOptimization>true", "WholeProgramOptimization>false")
            # Don't override the runtime library set by Conan's MSBuildToolchain
            replace_in_file(self, vcxproj_file, "<RuntimeLibrary>MultiThreaded</RuntimeLibrary>", "")
            replace_in_file(self, vcxproj_file, "<RuntimeLibrary>MultiThreadedDebug</RuntimeLibrary>", "")
        if is_msvc(self):
            msbuild = MSBuild(self)
            msbuild.build_type = (
                "Debug" if self.settings.build_type == "Debug" else "Release"
            )
            msbuild.platform = (
                "Win32" if self.settings.arch == "x86" else msbuild.platform
            )
            msbuild.build(sln="lzham.sln", targets=self._msvc_libs(targets=True))
        else:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder
        )

        if is_msvc(self):
            arch = "x86" if self.settings.arch == "x86" else "x64" 
            for target in self._msvc_libs():
                self.output.warning(target)
                debug_suffix = "D" if self.settings.build_type == "Debug" and not self.options.shared else ""
                arch_folder = f"{arch}{debug_suffix}"
                subfolder = "lib" if not target.endswith('dll') else "bin"
                subfolder_src = os.path.join("lib", arch_folder) if not target.endswith('dll') else "bin"
                self.output.warning(subfolder_src)
                copy(
                    self,
                    pattern=target,
                    dst=os.path.join(self.package_folder, subfolder),
                    src=os.path.join(self.build_folder, subfolder_src),
                    keep_path=False
                )
            copy(
                self,
                pattern="*.h",
                dst=os.path.join(self.package_folder, "include"),
                src=os.path.join(self.source_folder, "include"),
            )
        else:
            cmake = CMake(self)
            cmake.install()

            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            rmdir(self, os.path.join(self.package_folder, "res"))
            rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])

        if is_msvc(self):
            libs = list(set([filename[:-4] for filename in self._msvc_libs()]))
            self.cpp_info.libs = libs
        else:
            self.cpp_info.libs = ["lzhamdll", "lzhamcomp", "lzhamdecomp"]
            self.cpp_info.set_property("cmake_file_name", "lzham")
            self.cpp_info.set_property("cmake_target_name", "lzham::lzham")
            self.cpp_info.set_property("pkg_config_name", "lzham")

            # TODO: to remove in conan v2 once cmake_find_package_* generators
            # removed
            self.cpp_info.names["cmake_find_package"] = "lzham"
            self.cpp_info.names["cmake_find_package_multi"] = "lzham"
            self.cpp_info.names["pkg_config"] = "lzham"
