from conan import ConanFile
from conan.tools.files import copy, get, export_conandata_patches, apply_conandata_patches, replace_in_file, rm, rmdir
from conan.errors import ConanInvalidConfiguration
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.microsoft import VCVars
from conan.tools.microsoft import is_msvc
from conan.tools.apple import is_apple_os
from conan.tools.layout import basic_layout
from conan.tools.env import VirtualRunEnv, Environment
from os.path import join

required_conan_version = ">=1.60.0"

class NetSnmpConan(ConanFile):
    name = "net-snmp"
    description = (
        "Simple Network Management Protocol (SNMP) is a widely used protocol "
        "for monitoring the health and welfare of network equipment "
        "(eg. routers), computer equipment and even devices like UPSs."
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.net-snmp.org/"
    topics = "snmp"
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ipv6": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ipv6": True,
    }

    def validate(self):
        if self.settings.os == "Windows" and not is_msvc(self):
            raise ConanInvalidConfiguration("net-snmp is setup to build only with MSVC on Windows")

        if is_apple_os(self):
            raise ConanInvalidConfiguration("Building for Apple OS types not supported")


    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], filename=f"net-snmp-{self.version}.tar.gz", strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def requirements(self):
        self.requires("openssl/1.1.1q")
        self.requires("pcre/8.45")

    def build_requirements(self):
        if is_msvc(self):
            self.build_requires("strawberryperl/5.30.0.1")

    @property
    def _is_debug(self):
        return self.settings.build_type == "Debug"

    def generate(self):
        if is_msvc(self):
            self._generate_msvc()
        else:
            self._generate_unix()

    def build(self):
        apply_conandata_patches(self)

        if is_msvc(self):
            self._build_msvc()
        else:
            self._build_unix()

    def package(self):
        if is_msvc(self):
            self._package_msvc()
        else:
            self._package_unix()

        copy(self, "COPYING", src=self.source_folder, dst=join(self.package_folder, "licenses"), ignore_case=True)

    def package_info(self):
        self.cpp_info.libs = ["netsnmp"]
        self.cpp_info.requires = ["openssl::openssl", "pcre::pcre"]

        if self.settings.os == "Neutrino":
            self.cpp_info.system_libs.append("socket")

        if self.settings.os == "Neutrino" and self.settings.os.version == "7.1":
            self.cpp_info.system_libs.append("regex")
        
    def _generate_msvc(self):
        ms = VCVars(self)
        ms.generate()

    def _patch_msvc(self):
        ssl_info = self.dependencies["openssl"].cpp_info.aggregated_components()

        link_lines = "\n".join(
            f'#    pragma comment(lib, "{lib}.lib")'
            for lib in ssl_info.libs + ssl_info.system_libs
        )
        replace_in_file(self, join(self.source_folder, "win32", "net-snmp", "net-snmp-config.h.in"), "/* Conan: system_libs */", link_lines)

    def _build_msvc(self):
        self._patch_msvc()

        openssl_include_dir = join(self.dependencies["openssl"].package_folder, "include")
        openssl_lib_dir = join(self.dependencies["openssl"].package_folder, "lib")
        configure_folder = join(self.source_folder, "win32")
        config_type = "debug" if self._is_debug else "release"
        link_type = "dynamic" if self.options.shared else "static"
        self.run(f"perl Configure --config={config_type} --linktype={link_type} --with-ssl --with-sslincdir={openssl_include_dir} --with-ssllibdir={openssl_lib_dir} --prefix={self.build_folder}", cwd=f"{configure_folder}", env="conanbuild")
        self.run("nmake /nologo libs_clean libs install", cwd=f"{configure_folder}", env="conanbuild")

    def _package_msvc(self):
        cfg = "debug" if self._is_debug else "release"
        from_folder = join(self.source_folder,"win32", "bin", f"{cfg}")
        self.output.info(f"klaus {from_folder}")
        copy(self, "netsnmp.dll", dst=join(self.package_folder,"bin"), src=join(self.source_folder,"win32", "bin", f"{cfg}"))
        copy(self, "netsnmp.lib", dst=join(self.package_folder,"lib"), src=join(self.source_folder,"win32", "lib", f"{cfg}"))
        copy(self, "net-snmp/*", dst=join(self.package_folder, "include"), src=join(self.source_folder, "include"), keep_path=True)
        copy(self, "net-snmp/*", dst=join(self.package_folder, "include"), src=join(self.build_folder, "include"), keep_path=True)

    def _generate_unix(self):
        ad = AutotoolsDeps(self)
        ad.generate()

        pd = PkgConfigDeps(self)
        pd.generate()

        tc = AutotoolsToolchain(self)

        if self.settings.os in ["Linux"]:
            tc.extra_ldflags.append("-ldl")
            tc.extra_ldflags.append("-lpthread")

        if self.settings.os in ["Neutrino"]:
            tc.extra_ldflags.append("-ldl")
            tc.extra_ldflags.append("-lsocket")

            if self.settings.os.version == "7.1":
                tc.extra_ldflags.append("-lregex")

        tc.generate()

    def _build_unix(self):
        disabled_link_type = "static" if self.options.shared else "shared"
        debug_flag = "enable" if self._is_debug else "disable"
        ipv6_flag = "enable" if self.options.with_ipv6 else "disable"
        openssl_path = self.dependencies["openssl"].package_folder
        zlib_path = self.dependencies["zlib"].package_folder
        args = [
            f"--with-openssl={openssl_path}",
            f"--with-zlib={zlib_path}",
            "--with-defaults",
            "--without-rpm",
            "--disable-manuals",
            "--disable-scripts",
            "--disable-embedded-perl",
            f"--{debug_flag}-debugging",
            "--without-kmem-usage",
            "--with-out-mib-modules=mibII,ucd_snmp,agentx",
            f"--disable-{disabled_link_type}",
            f"--{ipv6_flag}-ipv6",
        ]

        if self.settings.os == "Neutrino":
            args.append("--with-endianness=little")

            if self.settings.os.version == "7.0":
                args.append("ac_cv_func_asprintf=no")


        autotools = Autotools(self)

        env = VirtualRunEnv(self)
        with env.vars().apply():
            autotools.configure(args=args)

        autotools.make()

    def _package_unix(self):
        autotools = Autotools(self)

        #only install with -j1 as parallel install will break dependencies. Probably a bug in the dependencies
        #install specific targets instead of just everything as it will try to do perl stuff on you host machine
        autotools.install(args=["-j1"], target="installsubdirs installlibs installprogs installheaders")

        rm(self, "*.la", join(self.package_folder, "lib"))
        rmdir(self, join(self.package_folder, "share"))
