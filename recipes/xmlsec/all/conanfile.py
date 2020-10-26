from conans import ConanFile, tools, AutoToolsBuildEnvironment
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
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")
        self.build_requires("libtool/2.4.6")
        self.build_requires("pkgconf/1.7.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "xmlsec-xmlsec-{}".format(self.version.replace('.', '_'))
        os.rename(extracted_folder, self._source_subfolder)
    
    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        yes_no = lambda v: "yes" if v else "no"
        configure_args = [
            "--enable-crypto-dl={}".format(yes_no(False)),
            "--enable-apps-crypto-dl={}".format(yes_no(False)),
            "--with-libxslt={}".format(yes_no(self.options.with_xslt)),
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        self._autotools.configure(args=configure_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        # FIXME: conan is missing a feature to change the join character on lists of environment variables
        # e.g. self.env_info.AUTOMAKE_CONAN_INCLUDES.joiner = ":"
        with tools.environment_append({"AUTOMAKE_CONAN_INCLUDES": tools.get_env("AUTOMAKE_CONAN_INCLUDES", "").replace(";", ":")}):
            with tools.chdir(self._source_subfolder):
                self.run("autoreconf -fiv", run_environment=True, win_bash=tools.os_info.is_windows)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("Copyright", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        os.remove(os.path.join(self.package_folder, "lib", "xmlsec1Conf.sh"))

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "xmlsec1"))
        self.cpp_info.defines.append("XMLSEC_CRYPTO_OPENSSL")
        if not self.options.with_xslt:
            self.cpp_info.defines.append("XMLSEC_NO_XSLT")
        self.cpp_info.defines.append("XMLSEC_NO_SIZE_T")
        self.cpp_info.libs = ["xmlsec1-openssl", "xmlsec1"]
        self.cpp_info.names["pkg_config"] = "xmlsec1"
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m", "dl", "pthread"]
