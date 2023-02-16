import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
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
            tc.generate()

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            msbuild = MSBuild(self)
            msbuild.build_type = (
                "Debug" if self.settings.build_type == "Debug" else "Release"
            )
            msbuild.platform = (
                "Win32" if self.settings.arch == "x86" else msbuild.platform
            )
            msbuild.build(sln="lzham.sln")
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
            suffix = "x64D" if self.settings.build_type == "Debug" else "x64"
            copy(
                self,
                pattern=f"lzham_{suffix}.lib",
                dst=os.path.join(self.package_folder, "lib"),
                src=os.path.join(self.build_folder, "lib", "x64"),
                keep_path=False
            )
            copy(
                self,
                pattern=f"lzham_{suffix}.dll",
                dst=os.path.join(self.package_folder, "bin"),
                src=os.path.join(self.build_folder, "bin"),
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
            lib_name = "lzham_x64"
            if self.settings.build_type == "Debug":
                lib_name += "D"
            self.cpp_info.libs = [lib_name]
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
