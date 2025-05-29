from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout
from conan.tools.microsoft import MSBuild, MSBuildDeps, MSBuildToolchain, is_msvc
import os


required_conan_version = ">=2.0"


class PackageConan(ConanFile):
    name = "package"
    description = "short description"
    # Use short name only, conform to SPDX License List: https://spdx.org/licenses/
    # In case not listed there, use "DocumentRef-<license-file-name>:LicenseRef-<package-name>"
    license = ""
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/project/package"
    # no "conan" and project name in topics. Use topics from the upstream listed on GH
    topics = ("topic1", "topic2", "topic3")
    # package_type should usually be "library", "shared-library" or "static-library"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": False,
    }

    # no exports_sources attribute, but export_sources(self) method instead
    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        # for plain C projects only. Otherwise, this method is not needed
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # Prefer self.requirements() method instead of self.requires attribute.
        self.requires("dependency/0.8.1")
        if self.options.with_foobar:
            # used in foo/baz.hpp:34
            self.requires("foobar/0.1.0")
        # A small number of dependencies on CCI are allowed to use version ranges.
        # See https://github.com/conan-io/conan-center-index/blob/master/docs/adding_packages/dependencies.md#version-ranges
        self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        # in case it does not work in another configuration, it should be validated here too
        # Always comment the reason including the upstream issue.
        # INFO: Upstream does not support DLL: See <URL>
        if not is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} can be built only by Visual Studio and msvc.")

    # if another tool than the compiler or CMake is required to build the project (pkgconf, bison, flex etc)
    def build_requirements(self):
        self.tool_requires("tool/x.y.z")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # apply patches listed in conandata.yml
        # Using patches is always the last resort to fix issues. If possible, try to fix the issue in the upstream project.
        apply_conandata_patches(self)

    @property
    def _msbuild_configuration(self):
        # Customize to Release when RelWithDebInfo or MinSizeRel, if upstream build files
        # don't have RelWithDebInfo and MinSizeRel.
        # Moreover:
        # - you may have to change these values if upstream build file uses custom configuration names.
        # - configuration of MSBuildToolchain/MSBuildDeps & build_type of MSBuild may have to be different.
        #   Its unusual, but it happens when there is a preSolution/postSolution mapping with different names.
        #   * build_type attribute of MSBuild should match preSolution
        #   * configuration attribute of MSBuildToolchain/MSBuildDeps should match postSolution
        return "Debug" if self.settings.build_type == "Debug" else "Release"

    def generate(self):
        tc = MSBuildToolchain(self)
        tc.configuration = self._msbuild_configuration
        tc.generate()

        # If there are requirements
        deps = MSBuildDeps(self)
        deps.configuration = self._msbuild_configuration
        deps.generate()

    def build(self):
        msbuild = MSBuild(self)
        msbuild.build_type = self._msbuild_configuration
        # customize according the solution file and compiler version
        msbuild.build(sln="project_2017.sln")

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.lib", self.source_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dll", self.source_folder, os.path.join(self.package_folder, "bin"), keep_path=False)
        copy(self, "*.h", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.libs = ["package_lib"]
