from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.env import Environment, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
import os


required_conan_version = ">=2.0.9"

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
        "with_foobar": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_foobar": True,
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
        # validate the minimum cpp standard supported. Only for C++ projects
        check_min_cppstd(self, 14)

        # Always comment the reason including the upstream issue.
        # INFO: Upstream only support Unix systems. See <URL>
        if self.settings.os not in ["Linux", "FreeBSD", "Macos"]:
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.settings.os}.")

    # if a tool other than the compiler or autotools is required to build the project (pkgconf, bison, flex etc)
    def build_requirements(self):
        # only if we have to call autoreconf
        self.tool_requires("libtool/x.y.z")
        # only if upstream configure.ac relies on PKG_CHECK_MODULES macro
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        # required to suppport windows as a build machine
        if self.settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        # for msvc support to get compile & ar-lib scripts (may be avoided if shipped in source code of the library)
        # not needed if libtool already in build requirements
        if is_msvc(self):
            self.tool_requires("automake/x.y.z")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # apply patches listed in conandata.yml
        # Using patches is always the last resort to fix issues. If possible, try to fix the issue in the upstream project.
        apply_conandata_patches(self)

    def generate(self):
        # inject required env vars into the build scope
        # it's required in case of native build when there is AutotoolsDeps & at least one dependency which might be shared, because configure tries to run a test executable
        if not cross_building(self):
            VirtualRunEnv(self).generate(scope="build")
        # --fpic is automatically managed when 'fPIC' option is declared
        # --enable/disable-shared is automatically managed when 'shared' option is declared
        tc = AutotoolsToolchain(self)
        # autotools usually uses 'yes' and 'no' to enable/disable options
        def yes_no(v): return "yes" if v else "no"
        tc.configure_args.extend([
            f"--with-foobar={yes_no(self.options.with_foobar)}",
            "--enable-tools=no",
            "--enable-manpages=no",
        ])
        tc.generate()
        # generate pkg-config files of dependencies (useless if upstream configure.ac doesn't rely on PKG_CHECK_MODULES macro)
        tc = PkgConfigDeps(self)
        tc.generate()
        # generate dependencies for autotools
        # some recipes might require a workaround for MSVC (https://github.com/conan-io/conan/issues/12784):
        # https://github.com/conan-io/conan-center-index/blob/00ce907b910d0d772f1c73bb699971c141c423c1/recipes/xapian-core/all/conanfile.py#L106-L135
        deps = AutotoolsDeps(self)
        deps.generate()

        # If Visual Studio is supported
        if is_msvc(self):
            env = Environment()
            # get compile & ar-lib from automake (or eventually lib source code if available)
            # it's not always required to wrap CC, CXX & AR with these scripts, it depends on how much love was put in
            # upstream build files
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} lib")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_msvc")

    def build(self):

        autotools = Autotools(self)
        # (optional) run autoreconf to regenerate configure file (libtool should be in tool_requires)
        autotools.autoreconf()
        # ./configure + toolchain file
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        # Some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        # Consider disabling these at first to verify that the package_info() output matches the info exported by the project.
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        # In shared lib/executable files, autotools set install_name (macOS) to lib dir absolute path instead of @rpath, it's not relocatable, so fix it
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["package_lib"]

        # if the package provides a pkgconfig file (package.pc, usually installed in <prefix>/lib/pkgconfig/)
        self.cpp_info.set_property("pkg_config_name", "package")

        # If they are needed on Linux, m, pthread and dl are usually needed on FreeBSD too
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])
