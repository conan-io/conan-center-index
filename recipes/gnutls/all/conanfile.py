from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, save
from conan.tools.gnu import AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps, Autotools
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import os
import textwrap

required_conan_version = ">=1.54.0"


class GnuTLSConan(ConanFile):
    name = "gnutls"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnutls.org"
    description = "GnuTLS is a secure communications library implementing the SSL, TLS and DTLS protocols"
    topics = ("tls", "ssl", "secure communications")
    license = ("LGPL-2.1-or-later", "GPL-3-or-later")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_cxx": [True, False],
        "enable_tools": [True, False],
        "enable_openssl_compatibility": [True, False],
        "with_zlib": [True, False],
        "with_zstd": [True, False],
        "with_brotli": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_cxx": True,
        "enable_tools": True,
        "enable_openssl_compatibility": False,
        "with_zlib": True,
        "with_zstd": True,
        "with_brotli": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.enable_cxx:
            self.settings.rm_safe("compiler.libcxx")
            self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("nettle/3.9.1")
        self.requires("gmp/6.3.0")
        self.requires("libiconv/1.17")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_zstd:
            self.requires("zstd/1.5.5")
        if self.options.with_brotli:
            self.requires("brotli/1.1.0")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} cannot be deployed by Visual Studio.")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.1.0")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        yes_no = lambda v: "yes" if v else "no"
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--disable-tests",
            "--disable-doc",
            "--disable-guile",
            "--disable-libdane",
            "--disable-manpages",
            "--disable-silent-rules",
            "--disable-full-test-suite",
            "--disable-maintainer-mode",
            "--disable-option-checking",
            "--disable-dependency-tracking",
            "--disable-heartbeat-support",
            "--disable-gtk-doc-html",
            "--without-p11-kit",
            "--disable-rpath",
            "--without-idn",
            "--with-included-unistring",
            "--with-included-libtasn1",
            "--with-libiconv-prefix={}".format(self.dependencies["libiconv"].package_folder),
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--with-cxx={}".format(yes_no(self.options.enable_cxx)),
            "--with-zlib={}".format(yes_no(self.options.with_zlib)),
            "--with-brotli={}".format(yes_no(self.options.with_brotli)),
            "--with-zstd={}".format(yes_no(self.options.with_zstd)),
            "--enable-tools={}".format(yes_no(self.options.enable_tools)),
            "--enable-openssl-compatibility={}".format(yes_no(self.options.enable_openssl_compatibility)),
        ])
        if is_apple_os(self):
            # fix_apple_shared_install_name() may fail without -headerpad_max_install_names
            # (see https://github.com/conan-io/conan-center-index/pull/15946#issuecomment-1464321305)
            tc.extra_ldflags.append("-headerpad_max_install_names")
        env = tc.environment()
        if cross_building(self):
            # INFO: Undefined symbols for architecture Mac arm64 rpl_malloc and rpl_realloc
            env.define("ac_cv_func_malloc_0_nonnull", "yes")
            env.define("ac_cv_func_realloc_0_nonnull", "yes")
        tc.generate(env)
        autodeps = AutotoolsDeps(self)
        autodeps.generate()
        pkgdeps = PkgConfigDeps(self)
        pkgdeps.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path)
        )

    def _create_cmake_module_variables(self, module_file):
        content = textwrap.dedent(f"""\
            set(GNUTLS_FOUND TRUE)
            if(NOT DEFINED GNUTLS_INCLUDE_DIR AND DEFINED GnuTLS_INCLUDE_DIRS)
                set(GNUTLS_INCLUDE_DIR ${{GnuTLS_INCLUDE_DIRS}})
            endif()
            if(NOT DEFINED GNUTLS_LIBRARIES AND DEFINED GnuTLS_LIBRARIES)
                set(GNUTLS_LIBRARIES ${{GnuTLS_LIBRARIES}})
            endif()
            if(NOT DEFINED GNUTLS_DEFINITIONS)
                if(DEFINED GnuTLS_DEFINITIONS)
                    set(GNUTLS_DEFINITIONS ${{GnuTLS_DEFINITIONS}})
                else()
                    set(GNUTLS_DEFINITIONS "")
                endif()
            endif()
            set(GNUTLS_VERSION {self.version})
        """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    def package_info(self):
        self.cpp_info.libs = ["gnutlsxx", "gnutls"] if self.options.enable_cxx else ["gnutls"]
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "GnuTLS")
        self.cpp_info.set_property("cmake_target_name", "GnuTLS::GnuTLS")
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path])
        self.cpp_info.set_property("pkg_config_name", "gnutls")

        if is_apple_os(self):
            self.cpp_info.frameworks = ["Security", "CoreFoundation"]
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "m"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "GnuTLS"
        self.cpp_info.names["cmake_find_package_multi"] = "GnuTLS"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        if self.options.enable_tools:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
