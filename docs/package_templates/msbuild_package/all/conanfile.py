from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc, MSBuildDeps, MSBuildToolchain, MSBuild, VCVars, unix_path
from conan.tools.layout import vs_layout
from conan.tools.files import apply_conandata_patches, get, copy, rm, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
import os


required_conan_version = ">=1.51.3"


class PackageConan(ConanFile):
    name = "package"
    description = "short description"
    license = "" # Use short name only, conform to SPDX License List: https://spdx.org/licenses/
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/project/package"
    topics = ("topic1", "topic2", "topic3") # no "conan" and project name in topics
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    # no exports_sources attribute, but export_sources(self) method instead
    # this allows finer grain exportation of patches per version
    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC # once removed by config_options, need try..except for a second del
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx # for plain C projects only
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd # for plain C projects only
        except Exception:
            pass

    def requirements(self):
        self.requires("dependency/0.8.1") # prefer self.requires method instead of requires attribute

    # if another tool than the compiler or CMake is required to build the project (pkgconf, bison, flex etc)
    def build_requirements(self):
        self.tool_requires("tool/x.y.z")

    def source(self):
        get(**self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def validate(self):
        # in case it does not work in another configuration, it should validated here too
        if not is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.name} can be built only by Visual Studio and msvc.")

    def layout(self):
        vs_layout(self, src_folder="src") # src_folder must use the same source folder name the project

    def generate(self):
        tc = MSBuildToolchain(self)
        tc.generate()
        tc = MSBuildDeps(self)
        tc.generate()
        tc = VCVars(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # remove bundled xxhash
        rm(self, "whateer.*", os.path.join(self.source_folder, "lib"))
        replace_in_file(
            self,
            os.path.join(self.source_folder, "CMakeLists.txt"),
            "...",
            "",
        )

    def build(self):
        self._patch_sources() # It can be apply_conandata_patches(self) only in case no more patches are needed
        msbuild = MSBuild(self)
        # customize to Release when RelWithDebInfo
        msbuild.build_type = "Debug" if self.settings.build_type == "Debug" else "Release"
        # use Win32 instead of the default value when building x86
        msbuild.platform = "Win32" if self.settings.arch == "x86" else msbuild.platform
        # customize according the solution file and compiler version
        msbuild.build(sln="project_2017.sln")

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="*.lib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        copy(self, pattern="*.dll", dst=os.path.join(self.package_folder, "bin"), src=self.build_folder, keep_path=False)
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        self.cpp_info.libs = ["package_lib"]
