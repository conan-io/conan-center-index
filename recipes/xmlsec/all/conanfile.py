from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import chdir, copy, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, NMakeDeps, NMakeToolchain
from conan.tools.scm import Version
import os

required_conan_version = ">=1.58.0"


class XmlSecConan(ConanFile):
    name = "xmlsec"
    description = "XML Security Library is a C library based on LibXML2. The library supports major XML security standards."
    license = ("MIT", "MPL-1.1")
    homepage = "https://www.aleksey.com/xmlsec"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("xml", "signature", "encryption")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
        "with_nss": [True, False],
        "with_gcrypt": [True, False],
        "with_gnutls": [True, False],
        "with_xslt": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_nss": False,
        "with_gcrypt": False,
        "with_gnutls": False,
        "with_openssl": True,
        "with_xslt": False,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libxml2/2.10.3")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1s")
        if self.options.with_xslt:
            self.requires("libxslt/1.1.34")

    def validate(self):
        if self.options.with_nss:
            raise ConanInvalidConfiguration("xmlsec with nss not supported yet in this recice")
        if self.options.with_gcrypt:
            raise ConanInvalidConfiguration("xmlsec with gcrypt not supported yet in this recice")
        if self.options.with_gnutls:
            raise ConanInvalidConfiguration("xmlsec with gnutls not supported yet in this recice")
        if not (self.options.with_openssl or self.options.with_nss or self.options.with_gcrypt or self.options.with_gnutls):
            raise ConanInvalidConfiguration("At least one crypto engine needs to be enabled")

    def build_requirements(self):
        if not is_msvc(self):
            self.tool_requires("libtool/2.4.7")
            if not self.conf.get("tools.gnu:pkg_config", check_type=str):
                self.tool_requires("pkgconf/1.9.3")
            if self._settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = NMakeToolchain(self)
            tc.generate()
            deps = NMakeDeps(self)
            deps.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()
            if not cross_building(self):
                env = VirtualRunEnv(self)
                env.generate(scope="build")

            tc = AutotoolsToolchain(self)
            if not self.options.shared:
                tc.extra_defines.append("XMLSEC_STATIC")
            yes_no = lambda v: "yes" if v else "no"
            tc.configure_args.extend([
                "--enable-crypto-dl=no",
                "--enable-apps-crypto-dl=no",
                f"--with-libxslt={yes_no(self.options.with_xslt)}",
                f"--with-openssl={yes_no(self.options.with_openssl)}",
                f"--with-nss={yes_no(self.options.with_nss)}",
                f"--with-nspr={yes_no(self.options.with_nss)}",
                f"--with-gcrypt={yes_no(self.options.with_gcrypt)}",
                f"--with-gnutls={yes_no(self.options.with_gnutls)}",
                "--enable-mscrypto=no",   # Built on mingw
                "--enable-mscng=no",      # Build on mingw
                "--enable-docs=no",
                "--enable-mans=no",
            ])
            tc.generate()

            deps = AutotoolsDeps(self)
            deps.generate()
            deps = PkgConfigDeps(self)
            deps.generate()

    def build(self):
        if is_msvc(self):
            # Configure step to generate Makefile.msvc
            deps_includedirs = []
            deps_libdirs = []
            for deps in self.dependencies.values():
                deps_cpp_info = deps.cpp_info.aggregated_components()
                deps_includedirs.extend(deps_cpp_info.includedirs)
                deps_libdirs.extend(deps_cpp_info.libdirs)

            crypto_engines = []
            if self.options.with_openssl:
                ov = Version(self.dependencies["openssl"].ref.version)
                crypto_engines.append(f"openssl={ov.major}{ov.minor}0")

            yes_no = lambda v: "yes" if v else "no"
            args = [
                f"prefix={self.package_folder}",
                f"cruntime=/{msvc_runtime_flag(self)}",
                f"debug={yes_no(self.settings.build_type == 'Debug')}",
                f"static={yes_no(not self.options.shared)}",
                "include=\"{}\"".format(";".join(deps_includedirs)),
                "lib=\"{}\"".format(";".join(deps_libdirs)),
                "with-dl=no",
                f"xslt={yes_no(self.options.with_xslt)}",
                "iconv=no",
                "crypto={}".format(",".join(crypto_engines)),
            ]

            with chdir(self, os.path.join(self.source_folder, "win32")):
                self.run(f"cscript configure.js {' '.join(args)}")

            # Fix library names in generated Makefile.msvc
            def format_libs(package):
                cpp_info = self.dependencies[package].cpp_info.aggregated_components()
                libs = [lib if lib.endswith(".lib") else f"{lib}.lib" for lib in cpp_info.libs + cpp_info.system_libs]
                return " ".join(libs)

            makefile_msvc = os.path.join(self.source_folder, "win32", "Makefile.msvc")
            replace_in_file(self, makefile_msvc, "libxml2.lib", format_libs("libxml2"))
            replace_in_file(self, makefile_msvc, "libxml2_a.lib", format_libs("libxml2"))
            if self.options.with_xslt:
                replace_in_file(self, makefile_msvc, "libxslt.lib", format_libs("libxslt"))
                replace_in_file(self, makefile_msvc, "libxslt_a.lib", format_libs("libxslt"))
            if self.options.with_openssl:
                replace_in_file(self, makefile_msvc, "libcrypto.lib", format_libs("openssl"))

            # Build with NMake
            with chdir(self, os.path.join(self.source_folder, "win32")):
                self.run("nmake -f Makefile.msvc")
        else:
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "Copyright", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            with chdir(self, os.path.join(self.source_folder, "win32")):
                self.run("nmake -f Makefile.msvc install")
            if not self.options.shared:
                rm(self, "*.dll", os.path.join(self.package_folder, "bin"))
            rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
            os.unlink(os.path.join(self.package_folder, "lib", "libxmlsec-openssl_a.lib" if self.options.shared else "libxmlsec-openssl.lib"))
            os.unlink(os.path.join(self.package_folder, "lib", "libxmlsec_a.lib" if self.options.shared else "libxmlsec.lib"))
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "share"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            os.remove(os.path.join(self.package_folder, "lib", "xmlsec1Conf.sh"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        major = str(Version(self.version).major)
        prefix = "lib" if is_msvc(self) else ""
        infix = "" if is_msvc(self) else major
        base_libname = f"{prefix}xmlsec{infix}"
        suffix = "_a" if is_msvc(self) and not self.options.shared else ""

        self.cpp_info.components["libxmlsec"].set_property("pkg_config_name", f"xmlsec{major}")
        self.cpp_info.components["libxmlsec"].libs = [f"{base_libname}{suffix}"]
        if not is_msvc(self):
            self.cpp_info.components["libxmlsec"].includedirs.append(os.path.join("include", f"xmlsec{major}"))
        self.cpp_info.components["libxmlsec"].requires = ["libxml2::libxml2"]
        if not self.options.shared:
            self.cpp_info.components["libxmlsec"].defines.append("XMLSEC_STATIC")
        if self.options.with_xslt:
            self.cpp_info.components["libxmlsec"].requires.append("libxslt::libxslt")
        else:
            self.cpp_info.components["libxmlsec"].defines.append("XMLSEC_NO_XSLT=1")
        self.cpp_info.components["libxmlsec"].defines.extend(["XMLSEC_NO_SIZE_T", "XMLSEC_NO_GOST=1", "XMLSEC_NO_CRYPTO_DYNAMIC_LOADING=1"])
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libxmlsec"].system_libs = ["m", "dl", "pthread"]
        if self.settings.os == "Windows":
            self.cpp_info.components["libxmlsec"].system_libs = ["crypt32", "ws2_32", "advapi32", "user32", "bcrypt"]

        if self.options.with_openssl:
            self.cpp_info.components["openssl"].set_property("pkg_config_name", f"xmlsec{major}-openssl")
            self.cpp_info.components["openssl"].libs = [f"{base_libname}-openssl{suffix}"]
            self.cpp_info.components["openssl"].requires = ["libxmlsec", "openssl::openssl"]
            self.cpp_info.components["openssl"].defines = ["XMLSEC_CRYPTO_OPENSSL=1"]
