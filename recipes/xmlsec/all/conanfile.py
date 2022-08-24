from conan.tools.microsoft import msvc_runtime_flag
from conans import ConanFile, tools, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment
from conan.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import functools
import os

required_conan_version = ">=1.36.0"


class XmlSecConan(ConanFile):
    name = "xmlsec"
    description = "XML Security Library is a C library based on LibXML2. The library supports major XML security standards."
    license = ("MIT", "MPL-1.1")
    homepage = "https://github.com/lsh123/xmlsec"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("xml", "signature", "encryption")

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

    generators = "pkg_config"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("libxml2/2.9.12")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1m")
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
        if not self._is_msvc:
            self.build_requires("libtool/2.4.6")
            self.build_requires("pkgconf/1.7.4")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @contextmanager
    def _msvc_build_environment(self):
        with tools.chdir(os.path.join(self._source_subfolder, "win32")):
            with tools.vcvars(self):
                with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                    yield

    def _build_msvc(self):
        yes_no = lambda v: "yes" if v else "no"
        with self._msvc_build_environment():
            crypto_engines = []
            if self.options.with_openssl:
                ov = tools.Version(self.deps_cpp_info["openssl"].version)
                crypto_engines.append("openssl={}{}0".format(ov.major, ov.minor))
            args = [
                "cscript",
                "configure.js",
                "prefix={}".format(self.package_folder),
                "cruntime=/{}".format(msvc_runtime_flag(self)),
                "debug={}".format(yes_no(self.settings.build_type == "Debug")),
                "static={}".format(yes_no(not self.options.shared)),
                "include=\"{}\"".format(";".join(self.deps_cpp_info.include_paths)),
                "lib=\"{}\"".format(";".join(self.deps_cpp_info.lib_paths)),
                "with-dl=no",
                "xslt={}".format(yes_no(self.options.with_xslt)),
                "iconv={}".format(yes_no(False)),
                "crypto={}".format(",".join(crypto_engines)),
            ]

            configure_command = " ".join(args)
            self.output.info(configure_command)
            self.run(configure_command)

            # Fix library names
            def format_libs(package):
                libs = []
                for lib in self.deps_cpp_info[package].libs:
                    libname = lib
                    if not libname.endswith(".lib"):
                        libname += ".lib"
                    libs.append(libname)
                for lib in self.deps_cpp_info[package].system_libs:
                    libname = lib
                    if not libname.endswith(".lib"):
                        libname += ".lib"
                    libs.append(libname)
                return " ".join(libs)

            tools.replace_in_file("Makefile.msvc", "libxml2.lib", format_libs("libxml2"))
            tools.replace_in_file("Makefile.msvc", "libxml2_a.lib", format_libs("libxml2"))
            if self.options.with_xslt:
                tools.replace_in_file("Makefile.msvc", "libxslt.lib", format_libs("libxslt"))
                tools.replace_in_file("Makefile.msvc", "libxslt_a.lib", format_libs("libxslt"))

            if self.settings.build_type == "Debug":
                tools.replace_in_file("Makefile.msvc", "libcrypto.lib", "libcryptod.lib")

            self.run("nmake /f Makefile.msvc")

    def _package_msvc(self):
        with self._msvc_build_environment():
            self.run("nmake /f Makefile.msvc install")

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if not self.options.shared:
            autotools.defines.append("XMLSEC_STATIC")
        yes_no = lambda v: "yes" if v else "no"
        configure_args = [
            "--enable-crypto-dl={}".format(yes_no(False)),
            "--enable-apps-crypto-dl={}".format(yes_no(False)),
            "--with-libxslt={}".format(yes_no(self.options.with_xslt)),
            "--with-openssl={}".format(yes_no(self.options.with_openssl)),
            "--with-nss={}".format(yes_no(self.options.with_nss)),
            "--with-nspr={}".format(yes_no(self.options.with_nss)),
            "--with-gcrypt={}".format(yes_no(self.options.with_gcrypt)),
            "--with-gnutls={}".format(yes_no(self.options.with_gnutls)),
            "--enable-mscrypto={}".format(yes_no(False)),   # Built on mingw
            "--enable-mscng={}".format(yes_no(False)),      # Build on mingw
            "--enable-docs=no",
            "--enable-mans=no",
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        autotools.libs = []
        autotools.configure(args=configure_args, configure_dir=self._source_subfolder)
        return autotools

    def build(self):
        if self._is_msvc:
            self._build_msvc()
        else:
            with tools.chdir(self._source_subfolder):
                self.run("{} -fiv".format(tools.get_env("AUTORECONF")), run_environment=True, win_bash=tools.os_info.is_windows)
                # relocatable shared lib on macOS
                tools.replace_in_file("configure", "-install_name \\$rpath/", "-install_name @rpath/")
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("Copyright", src=self._source_subfolder, dst="licenses")

        if self._is_msvc:
            self._package_msvc()
            if not self.options.shared:
                tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.dll")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")
            os.unlink(os.path.join(self.package_folder, "lib", "libxmlsec-openssl_a.lib" if self.options.shared else "libxmlsec-openssl.lib"))
            os.unlink(os.path.join(self.package_folder, "lib", "libxmlsec_a.lib" if self.options.shared else "libxmlsec.lib"))
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "share"))
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            os.remove(os.path.join(self.package_folder, "lib", "xmlsec1Conf.sh"))

    def package_info(self):
        prefix = "lib" if self._is_msvc else ""
        infix = "" if self._is_msvc else str(tools.Version(self.version).major)
        suffix = "_a" if self._is_msvc and not self.options.shared else ""

        get_libname = lambda libname: prefix + "xmlsec" + infix + (("-" + libname) if libname else "") + suffix

        self.cpp_info.components["libxmlsec"].libs = [get_libname(None)]
        self.cpp_info.components["libxmlsec"].includedirs.append(os.path.join("include", "xmlsec{}".format(tools.Version(self.version).major)))
        self.cpp_info.components["libxmlsec"].requires = ["libxml2::libxml2"]
        self.cpp_info.components["libxmlsec"].set_property(
            "pkg_config_name", "xmlsec{}".format(tools.Version(self.version).major)
        )
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
            self.cpp_info.components["openssl"].libs = [get_libname("openssl")]
            self.cpp_info.components["openssl"].requires = ["libxmlsec", "openssl::openssl"]
            self.cpp_info.components["openssl"].defines = ["XMLSEC_CRYPTO_OPENSSL=1"]
            self.cpp_info.components["openssl"].set_property(
                "pkg_config_name", "xmlsec{}-openssl".format(tools.Version(self.version).major)
            )
