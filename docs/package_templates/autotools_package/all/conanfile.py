from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
import os


required_conan_version = ">=1.52.0"

#
# INFO: Please, remove all comments before pushing your PR!
#


class PackageConan(ConanFile):
    name = "package"
    description = "short description"
    # Use short name only, conform to SPDX License List: https://spdx.org/licenses/
    # In case not listed there, use "LicenseRef-<license-file-name>"
    license = ""
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/project/package"
    # no "conan" and project name in topics. Use topics from the upstream listed on GH
    topics = ("topic1", "topic2", "topic3")
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

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    # no exports_sources attribute, but export_sources(self) method instead
    # this allows finer grain exportation of patches per version
    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                # once removed by config_options, need try..except for a second del
                del self.options.fPIC
            except Exception:
                pass
        # for plain C projects only
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        # src_folder must use the same source folder name the project
        basic_layout(self, src_folder="src")

    def requirements(self):
        # prefer self.requires method instead of requires attribute
        self.requires("dependency/0.8.1")
        if self.options.with_foobar:
            self.requires("foobar/0.1.0")

    def validate(self):
        # validate the minimum cpp standard supported. Only for C++ projects
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        if self.info.settings.os not in ["Linux", "FreeBSD", "MacOS"]:
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.info.settings.os}.")

    # if another tool than the compiler or autotools is required to build the project (pkgconf, bison, flex etc)
    def build_requirements(self):
        # only if we have to call autoreconf
        self.tool_requires("libtool/x.y.z")
        # only if upstream configure.ac relies on PKG_CHECK_MODULES macro
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/x.y.z")
        # required to suppport windows as a build machine
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=str):
                self.tool_requires("msys2/cci.latest")
        # for msvc support to get compile & ar-lib scripts (may be avoided if shipped in source code of the library)
        if is_msvc(self):
            self.tool_requires("automake/x.y.z")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        # inject tools_requires env vars in build scope (not needed if there is no tool_requires)
        env = VirtualBuildEnv(self)
        env.generate()
        # inject requires env vars in build scope
        # it's required in case of native build when there is AutotoolsDeps & at least one dependency which might be shared, because configure tries to run a test executable
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        # --fpic is automatically managed when 'fPIC'option is declared
        # --enable/disable-shared is automatically managed when 'shared' option is declared
        tc = AutotoolsToolchain(self)
        # autotools usually uses 'yes' and 'no' to enable/disable options
        yes_no = lambda v: "yes" if v else "no"
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
        tc = AutotoolsDeps(self)
        tc.generate()

        # If Visual Studio is supported
        if is_msvc(self):
            env = Environment()
            # get compile & ar-lib from automake (or eventually lib source code if available)
            # it's not always required to wrap CC, CXX & AR with these scripts, it depends on how much love was put in
            # upstream build files
            compile_wrapper = unix_path(self, self._user_info_build["automake"].compile)
            ar_wrapper = unix_path(self, self._user_info_build["automake"].ar_lib)
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} \"lib -nologo\"")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_msvc")

    def build(self):
        # apply patches listed in conandata.yml
        apply_conandata_patches(self)
        autotools = Autotools(self)
        # (optional) run autoreconf to regenerate configure file (libtool should be in tool_requires)
        autotools.autoreconf()
        # ./configure + toolchain file
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        # TODO: replace by autotools.install() once https://github.com/conan-io/conan/issues/12153 fixed
        autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])

        # some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        # In shared lib/executable files, autotools set install_name (macOS) to lib dir absolute path instead of @rpath, it's not relocatable, so fix it
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["package_lib"]

        # if package provides a pkgconfig file (package.pc, usually installed in <prefix>/lib/pkgconfig/)
        self.cpp_info.set_property("pkg_config_name", "package")

        # If they are needed on Linux, m, pthread and dl are usually needed on FreeBSD too
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])
