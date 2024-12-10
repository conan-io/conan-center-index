from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc
import os


required_conan_version = ">=2.0"

#
# INFO: Please, remove all comments before pushing your PR!
#


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
        "fPIC": [True, False],
        "feature": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "feature": True,
    }
    # In case having config_options() or configure() method, the logic should be moved to the specific methods.
    implements = ["auto_shared_fpic"]

    # no exports_sources attribute, but export_sources(self) method instead
    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        # Keep this logic only in case configure() is needed e.g pure-c project.
        # Otherwise remove configure() and auto_shared_fpic will manage it.
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # for plain C projects only. Otherwise, remove this method.
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # Prefer self.requirements() method instead of self.requires attribute.
        self.requires("dependency/0.8.1")
        if self.options.with_foobar:
            # INFO: used in foo/baz.hpp:34
            self.requires("foobar/0.1.0")
        # Some dependencies on CCI are allowed to use version ranges.
        # See https://github.com/conan-io/conan-center-index/blob/master/docs/adding_packages/dependencies.md#version-ranges
        self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        # validate the minimum cpp standard supported. For C++ projects only
        check_min_cppstd(self, 14)
        # in case it does not work in another configuration, it should be validated here too
        # Always comment the reason including the upstream issue.
        # INFO: Upstream does not support DLL: See <URL>
        if is_msvc(self) and self.info.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Visual Studio and msvc.")

    # if another tool than the compiler or Meson is required to build the project (pkgconf, bison, flex etc)
    def build_requirements(self):
        # CCI policy assumes that Meson may not be installed on consumers machine
        self.tool_requires("meson/[>=1.2.3 <2]")
        # pkgconf is largely used by Meson, it should be added in build requirement when there are dependencies
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # apply patches listed in conandata.yml
        # Using patches is always the last resort to fix issues. If possible, try to fix the issue in the upstream project.
        apply_conandata_patches(self)

    def generate(self):
        # Meson feature options must be set to "enabled" or "disabled"
        def feature(v): return "enabled" if v else "disabled"
        # default_library and static and fpic are automatically parsed when self.options.shared and self.options.fpic exist
        # buildtype is automatically parsed for self.settings
        tc = MesonToolchain(self)
        # In case need to pass definitions directly to the compiler
        tc.preprocessor_definitions["MYDEFINE"] = "MYDEF_VALUE"
        # Meson features are typically enabled automatically when possible.
        # The default behavior can be changed to disable all features by setting "auto_features" to "disabled".
        tc.project_options["auto_features"] = "disabled"
        tc.project_options["feature"] = feature(self.options.get_safe("feature"))
        # Meson project options may vary their types
        tc.project_options["tests"] = False
        tc.generate()
        # In case there are dependencies listed under requirements, PkgConfigDeps should be used
        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()

        # Some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        # Consider disabling these at first to verify that the package_info() output matches the info exported by the project.
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

        # In shared lib/executable files, meson set install_name (macOS) to lib dir absolute path instead of @rpath, it's not relocatable, so fix it
        fix_apple_shared_install_name(self)

    def package_info(self):
        # avoid collect_libs(), prefer explicit library name instead
        self.cpp_info.libs = ["package_lib"]
        # if package provides a pkgconfig file (package.pc, usually installed in <prefix>/lib/pkgconfig/)
        self.cpp_info.set_property("pkg_config_name", "package")
        # If they are needed on Linux, m, pthread and dl are usually needed on FreeBSD too
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "dl"])
