from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, rm, rmdir, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import unix_path, is_msvc, MSBuildDeps, MSBuildToolchain, MSBuild
import os

required_conan_version = ">=1.54.0"


class CyrusSaslConan(ConanFile):
    name = "cyrus-sasl"
    license = "BSD-4-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.cyrusimap.org/sasl/"
    description = (
        "This is the Cyrus SASL API implementation. "
        "It can be used on the client or server side "
        "to provide authentication and authorization services."
    )
    topics = ("sasl", "authentication", "authorization")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
        "with_cram": [True, False],
        "with_digest": [True, False],
        "with_scram": [True, False],
        "with_otp": [True, False],
        "with_krb4": [True, False],
        "with_gssapi": [True, False],
        "with_plain": [True, False],
        "with_anon": [True, False],
        "with_postgresql": [True, False],
        "with_mysql": [True, False],
        "with_sqlite3": [True, False],
        "with_saslauthd": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": True,
        "with_cram": True,
        "with_digest": True,
        "with_scram": True,
        "with_otp": True,
        "with_krb4": True,
        "with_gssapi": False, # FIXME: should be True
        "with_plain": True,
        "with_anon": True,
        "with_postgresql": False,
        "with_mysql": False,
        "with_sqlite3": False,
        "with_saslauthd": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            # saslauthd doesn't compile on Windows
            # https://www.cyrusimap.org/sasl/sasl/windows.html#install-windows
            del self.options.with_saslauthd
        if is_msvc(self):
            # always required
            del self.options.with_openssl
            # not used
            del self.options.with_postgresql
            del self.options.with_mysql
            del self.options.with_sqlite3

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if is_msvc(self) or self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")
        if self.options.get_safe("with_postgresql"):
            self.requires("libpq/15.4")
        if self.options.get_safe("with_mysql"):
            self.requires("libmysqlclient/8.1.0")
        if self.options.get_safe("with_sqlite3"):
            self.requires("sqlite3/3.44.2")

    def validate(self):
        if is_msvc(self) and not self.options.shared:
            raise ConanInvalidConfiguration("Static library output is not supported when building with MSVC")
        if self.options.with_gssapi:
            raise ConanInvalidConfiguration(
                f"{self.name}:with_gssapi=True requires krb5 recipe, not yet available in conan-center",
            )

    def build_requirements(self):
        if not is_msvc(self):
            self.tool_requires("gnu-config/cci.20210814")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _generate_autotools(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        rootpath_no = lambda v, req: unix_path(self, self.dependencies[req].package_folder) if v else "no"
        tc.configure_args.extend([
            "--disable-sample",
            "--disable-macos-framework",
            "--with-dblib=none",
            "--with-openssl={}".format(yes_no(self.options.with_openssl)),
            "--enable-digest={}".format(yes_no(self.options.with_digest)),
            "--enable-scram={}".format(yes_no(self.options.with_scram)),
            "--enable-otp={}".format(yes_no(self.options.with_otp)),
            "--enable-krb4={}".format(yes_no(self.options.with_krb4)),
            "--enable-gssapi={}".format(yes_no(self.options.with_gssapi)),
            "--enable-plain={}".format(yes_no(self.options.with_plain)),
            "--enable-anon={}".format(yes_no(self.options.with_anon)),
            "--enable-sql={}".format(
                yes_no(self.options.with_postgresql or self.options.with_mysql or self.options.with_sqlite3),
            ),
            "--with-pgsql={}".format(rootpath_no(self.options.with_postgresql, "libpq")),
            "--with-mysql={}".format(rootpath_no(self.options.with_mysql, "libmysqlclient")),
            "--without-sqlite",
            "--with-sqlite3={}".format(rootpath_no(self.options.with_sqlite3, "sqlite3")),
            "--with-saslauthd={}".format(yes_no(self.options.with_saslauthd)),
        ])
        if self.options.with_gssapi:
            tc.configure_args.append("--with-gss_impl=mit")
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

    def _patch_sources_autotools(self):
        for gnu_config in [
            self.conf.get("user.gnu-config:config_guess", check_type=str),
            self.conf.get("user.gnu-config:config_sub", check_type=str),
        ]:
            if gnu_config:
                copy(self, os.path.basename(gnu_config),
                     src=os.path.dirname(gnu_config),
                     dst=os.path.join(self.source_folder, "config"))

    def _build_autotools(self):
        self._patch_sources_autotools()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    @property
    def _msbuild_configuration(self):
        return "Debug" if self.settings.build_type == "Debug" else "Release"

    def _generate_msvc(self):
        tc = MSBuildToolchain(self)
        tc.configuration = self._msbuild_configuration
        # disable OpenSSL 3 warnings, which get raised as errors
        tc.cxxflags.append("/wo4996")
        tc.generate()

        deps = MSBuildDeps(self)
        deps.configuration = self._msbuild_configuration
        deps.generate()

    def _patch_sources_msvc(self):
        # TODO: to remove once https://github.com/conan-io/conan/pull/12817 available in conan client
        platform_toolset = MSBuildToolchain(self).toolset
        import_conan_generators = ""
        for props_file in ["conantoolchain.props", "conandeps.props"]:
            props_path = os.path.join(self.generators_folder, props_file)
            if os.path.exists(props_path):
                import_conan_generators += f"<Import Project=\"{props_path}\" />"
        for vcxproj_file in self.source_path.joinpath("win32").glob("*.vcxproj"):
            replace_in_file(self, vcxproj_file,
                            "<PlatformToolset>v140</PlatformToolset>",
                            f"<PlatformToolset>{platform_toolset}</PlatformToolset>")
            replace_in_file(self, vcxproj_file, "<WindowsTargetPlatformVersion>8.1</WindowsTargetPlatformVersion>", "")
            if props_path:
                replace_in_file(self, vcxproj_file,
                                '<Import Project="$(VCTargetsPath)\\Microsoft.Cpp.targets" />',
                                f'{import_conan_generators}<Import Project="$(VCTargetsPath)\\Microsoft.Cpp.targets" />')
        replace_in_file(self, os.path.join(self.source_folder, "win32", "openssl.props"),
                        "libeay32.lib;", "")
        # https://github.com/cyrusimap/cyrus-sasl/issues/730
        copy(self, "md5global.h",
             src=os.path.join(self.source_folder, "win32", "include"),
             dst=os.path.join(self.source_folder, "include"))

    def _build_msvc(self):
        self._patch_sources_msvc()
        msbuild = MSBuild(self)
        msbuild.build_type = self._msbuild_configuration
        msbuild.build(sln=os.path.join(self.source_folder, "win32", "cyrus-sasl-common.sln"))
        msbuild.build(sln=os.path.join(self.source_folder, "win32", "cyrus-sasl-core.sln"))
        # TODO: add sasldb support
        # msbuild.build(sln=os.path.join(self.source_folder, "win32", "cyrus-sasl-sasldb.sln"))
        if self.options.with_gssapi:
            msbuild.build(sln=os.path.join(self.source_folder, "win32", "cyrus-sasl-gssapiv2.sln"))

    def generate(self):
        if is_msvc(self):
            self._generate_msvc()
        else:
            self._generate_autotools()

    def build(self):
        if is_msvc(self):
            self._build_msvc()
        else:
            self._build_autotools()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            copy(self, "*/sasl2.lib", os.path.join(self.source_folder, "win32"), os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*/sasl2.dll", os.path.join(self.source_folder, "win32"), os.path.join(self.package_folder, "bin"), keep_path=False)
            copy(self, "*.h", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include", "sasl"))
        else:
            autotools = Autotools(self)
            autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"), recursive=True)
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libsasl2")
        self.cpp_info.libs = ["sasl2"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["resolv"]
            if self.options.with_saslauthd:
                self.cpp_info.system_libs.append("crypt")
        elif is_msvc(self):
            self.cpp_info.system_libs = ["ws2_32"]

        # TODO: to remove in conan v2
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
