import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.microsoft import MSBuild, MSBuildDeps, MSBuildToolchain, VCVars, check_min_vs, is_msvc, vs_layout

required_conan_version = ">=1.53.0"


class CppWinRtConan(ConanFile):
    name = "cppwinrt"
    description = "C++17 language projection for Windows Runtime"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/microsoft/cppwinrt"
    topics = ("native", "cpp", "winrt")
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        vs_layout(self)

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        self.requires("winmd/1.0.210629.2")

    @property
    def _min_cppstd(self):
        return 17

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 192)
        if not is_msvc(self):
            raise ConanInvalidConfiguration(
                f"{self.ref} can be built only by Visual Studio and msvc.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = MSBuildToolchain(self)
        tc.properties["WindowsTargetPlatformVersion"] = "10.0"
        tc.properties["WindowsTargetPlatformMinVersion"] = "10.0.17763.0"
        tc.generate()
        tc = MSBuildDeps(self)
        tc.generate()
        tc = VCVars(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        msbuild = MSBuild(self)
        # use Win32 instead of the default value when building x86
        msbuild.platform = "Win32" if self.info.settings.arch == "x86" else msbuild.platform
        build_folder = os.path.join(self.build_folder, "_build", msbuild.platform, str(
            self.info.settings.build_type))
        self.run(" ".join([msbuild.command(sln="cppwinrt.sln", targets=[
                 "prebuild", "cppwinrt"]), f"/p:CppWinRTBuildVersion={self.version}"]))
        self.run(" ".join([os.path.join(build_folder, "cppwinrt.exe"),
                           "-in", "local", "-out", build_folder, "-verbose"]))

    def package(self):
        msbuild = MSBuild(self)
        build_folder = os.path.join(self.build_folder, "_build", msbuild.platform, str(
            self.info.settings.build_type))

        copy(self, pattern="LICENSE", dst=os.path.join(
            self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self, pattern="cppwinrt.exe", dst=os.path.join(self.package_folder, "bin"), src=build_folder, keep_path=False
        )
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(build_folder),
            excludes="strings.h"
        )

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "Microsoft::CppWinRT")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "cppwinrt"
        self.cpp_info.filenames["cmake_find_package_multi"] = "cppwinrt"
        self.cpp_info.names["cmake_find_package"] = "Microsoft"
        self.cpp_info.names["cmake_find_package_multi"] = "Microsoft"

        self.cpp_info.components["cppwinrt"].names["cmake_find_package"] = "CppWinRT"
        self.cpp_info.components["cppwinrt"].names["cmake_find_package_multi"] = "CppWinRT"
        self.cpp_info.components["cppwinrt"].set_property(
            "cmake_target_name", "Microsoft::CppWinRT")

        # TODO: Legacy, to be removed on Conan 2.0
        bin_folder = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_folder)
