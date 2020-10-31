from conans import ConanFile, tools, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment
from contextlib import contextmanager
import os

class XmlSecConan(ConanFile):
    name = "xmlsec"
    description = "XML Security Library is a C library based on LibXML2. The library supports major XML security standards."
    license = ("MIT", "MPL-1.1")
    homepage = "https://github.com/lsh123/xmlsec"
    url = "https://github.com/conan-io/conan-center-index"
    generators = "pkg_config"
    settings = "os", "compiler", "arch", "build_type"
    topics = ("xml", "signature", "encryption")
    options = {
        "shared": [True, False], 
        "fPIC": [True, False],
        "with_xslt": [True, False]
        }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_xslt": False
        }
    
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("libxml2/2.9.10")
        self.requires("openssl/1.1.1h")
        if self.options.with_xslt:
            self.requires("libxslt/1.1.34")
    
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        
    def build_requirements(self):
        if self.settings.compiler != "Visual Studio" and tools.os_info.is_windows and os.environ.get("CONAN_BASH_PATH", None) is None:
            self.build_requires("msys2/20200517")
        self.build_requires("libtool/2.4.6")
        self.build_requires("pkgconf/1.7.3")

    @property
    def _is_msvc(self):
        return self.settings.compiler == 'Visual Studio'

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "xmlsec-xmlsec-{}".format(self.version.replace('.', '_'))
        os.rename(extracted_folder, self._source_subfolder)
    
    @contextmanager
    def _msvc_build_environment(self):
        with tools.chdir(os.path.join(self._source_subfolder, 'win32')):
            with tools.vcvars(self.settings):
                with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                    yield

    def _build_msvc(self):
        with self._msvc_build_environment():
            debug = "yes" if self.settings.build_type == "Debug" else "no"
            static = "no" if self.options.shared else "yes"

            args = ["cscript",
                    "configure.js",
                    "prefix=%s" % self.package_folder,
                    "cruntime=/%s" % self.settings.compiler.runtime,
                    "debug=%s" % debug,
                    "static=%s" % static,
                    'include="%s"' % ";".join(self.deps_cpp_info.include_paths),
                    'lib="%s"' % ";".join(self.deps_cpp_info.lib_paths),
                    'with-dl=no',
                    "xslt=%s" % ("yes" if self.options.with_xslt else "no"),
                    'iconv=no']

            configure_command = ' '.join(args)
            self.output.info(configure_command)
            self.run(configure_command)

            # Fix library names
            def format_libs(package):
                libs = []
                for lib in self.deps_cpp_info[package].libs:
                    libname = lib
                    if not libname.endswith('.lib'):
                        libname += '.lib'
                    libs.append(libname)
                for lib in self.deps_cpp_info[package].system_libs:
                    libname = lib
                    if not libname.endswith('.lib'):
                        libname += '.lib'
                    libs.append(libname)
                return ' '.join(libs)

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

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        full_install_subfolder = tools.unix_path(self.package_folder) if tools.os_info.is_windows else self.package_folder
        yes_no = lambda v: "yes" if v else "no"
        configure_args = [
            "--prefix=%s" % full_install_subfolder,
            "--enable-crypto-dl={}".format(yes_no(False)),
            "--enable-apps-crypto-dl={}".format(yes_no(False)),
            "--with-libxslt={}".format(yes_no(self.options.with_xslt)),
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        self._autotools.configure(args=configure_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        if self._is_msvc:
            self._build_msvc()
        else:
            # FIXME: conan is missing a feature to change the join character on lists of environment variables
            # e.g. self.env_info.AUTOMAKE_CONAN_INCLUDES.joiner = ":"
            with tools.environment_append({"AUTOMAKE_CONAN_INCLUDES": tools.get_env("AUTOMAKE_CONAN_INCLUDES", "").replace(";", ":")}):
                with tools.chdir(self._source_subfolder):
                    self.run("autoreconf -fiv", run_environment=True, win_bash=tools.os_info.is_windows)
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("Copyright", src=self._source_subfolder, dst="licenses")
        
        if self._is_msvc:
            self._package_msvc()
            if not self.options.shared:
                tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.dll")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")
            os.unlink(os.path.join(self.package_folder, 'lib', 'libxmlsec-openssl_a.lib' if self.options.shared else 'libxmlsec-openssl.lib'))
            os.unlink(os.path.join(self.package_folder, 'lib', 'libxmlsec_a.lib' if self.options.shared else 'libxmlsec.lib'))
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "share"))
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            os.remove(os.path.join(self.package_folder, "lib", "xmlsec1Conf.sh"))

    def package_info(self):
        if self._is_msvc:
            if self.options.shared:
                self.cpp_info.libs = ["libxmlsec-openssl", "libxmlsec"]
            else: 
                self.cpp_info.libs = ["libxmlsec-openssl_a", "libxmlsec_a"]
        else:
            self.cpp_info.libs = ["xmlsec1-openssl", "xmlsec1"]
        self.cpp_info.includedirs.append(os.path.join("include", "xmlsec1"))
        self.cpp_info.defines.append("XMLSEC_CRYPTO_OPENSSL")
        if not self.options.with_xslt:
            self.cpp_info.defines.append("XMLSEC_NO_XSLT")
        self.cpp_info.defines.append("XMLSEC_NO_SIZE_T")
        if not self.options.shared:
            self.cpp_info.defines.append("XMLSEC_STATIC")
        self.cpp_info.names["pkg_config"] = "xmlsec1"
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m", "dl", "pthread"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["crypt32", "ws2_32", "advapi32", "user32", "bcrypt"]
