import os
import functools
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration


class GnuTLSConan(ConanFile):
    name = "gnutls"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnutls.org"
    description = "GnuTLS is a secure communications library implementing the SSL, TLS and DTLS protocols"
    license = "LGPL-2.1"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'fPIC': True}
    generators = "pkg_config"
    _configure_vars = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.os == "Windows" and self.settings.compiler in ("Visual Studio", "msvc"):
            raise ConanInvalidConfiguration("The GnuTLS package cannot be deployed by Visual Studio.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def requirements(self):
        self.requires("nettle/3.5")
        self.requires("gmp/6.2.1")
        self.requires("libiconv/1.16")

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        configure_args = ["--disable-tests",
                          "--disable-doc",
                          "--disable-manpages",
                          "--disable-full-test-suite",
                          "--disable-maintainer-mode",
                          "--disable-option-checking",
                          "--without-p11-kit",
                          "--without-idn",
                          "--with-included-libtasn1",
                          "--with-included-unistring",
                          "--with-libiconv-prefix={}".format(self.deps_cpp_info["libiconv"].rootpath)]
        self._configure_vars = autotools.vars
        self._configure_vars.update({
            "NETTLE_CFLAGS": "-I{}".format(self.deps_cpp_info["nettle"].include_paths[0]),
            "NETTLE_LIBS": "-L{} -lnettle".format(self.deps_cpp_info["nettle"].lib_paths[0]),
            "HOGWEED_CFLAGS": "-I{}".format(self.deps_cpp_info["nettle"].include_paths[0]),
            "HOGWEED_LIBS": "-L{} -lhogweed".format(self.deps_cpp_info["nettle"].lib_paths[0]),
            "GMP_CFLAGS": "-I{}".format(self.deps_cpp_info["gmp"].include_paths[0]),
            "GMP_LIBS": "-L{} -lgmp".format(self.deps_cpp_info["gmp"].lib_paths[0]),
        })

        if self.options.shared:
            configure_args.extend(["--enable-shared", "--disable-static"])
        else:
            configure_args.extend(["--disable-shared", "--enable-static"])
        autotools.configure(args=configure_args, configure_dir=self._source_subfolder, vars=self._configure_vars)
        return autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make(vars=self._configure_vars)

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        # tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        self.cpp_info.set_property("cmake_file_name", "GnuTLS")
        self.cpp_info.set_property("cmake_target_name", "GnuTLS")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "GnuTLS"
        self.cpp_info.names["cmake_find_package_multi"] = "GnuTLS"
