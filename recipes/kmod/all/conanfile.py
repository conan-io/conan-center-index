from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
import os

required_conan_version = ">=1.44"

class KModConan(ConanFile):
    name = "kmod"
    description = "linux kernel module handling library"
    topics = ("kmod", "libkmod", "linux", "kernel", "module")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kmod-project/kmod"
    license = "LGPL-2.1-only"
    settings = "os", "arch", "compiler", "build_type"
    tool_requires = 'libtool/2.4.6', 'pkgconf/1.7.4'
    options = {
        "fPIC": [True, False],
        "with_zstd": [True, False],
        "with_xz": [True, False],
        "with_zlib": [True, False],
        "with_openssl": [True, False],
        "experimental": [True, False],
        "logging": [True, False],
    }
    default_options = {
        "fPIC": True,
        "with_zstd": True,
        "with_xz": True,
        "with_zlib": True,
        "with_openssl": True,
        "experimental": False,
        "logging": False,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def generate(self):
        yes_no = lambda v: "yes" if v else "no"
        tc = AutotoolsToolchain(self)
        tc.default_configure_install_args = True  # FIXME: https://github.com/conan-io/conan/issues/10650 (should be default)
        tc.configure_args.append("--with-zstd=%s" % yes_no(self.options.with_zstd))
        tc.configure_args.append("--with-xz=%s" % yes_no(self.options.with_xz))
        tc.configure_args.append("--with-zlib=%s" % yes_no(self.options.with_zlib))
        tc.configure_args.append("--with-openssl=%s" % yes_no(self.options.with_openssl))
        tc.configure_args.append("--enable-experimental=%s" % yes_no(self.options.experimental))
        tc.configure_args.append("--enable-logging=%s" % yes_no(self.options.logging))
        tc.configure_args.append("--enable-debug=%s" % yes_no(self.settings.build_type == "Debug"))
        tc.configure_args.append("--enable-tools=no")
        tc.configure_args.append("--enable-manpages=no")
        tc.configure_args.append("--enable-test-modules=no")
        tc.configure_args.append("--enable-python=no")
        tc.configure_args.append("--enable-coverage=no")
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()
        tc = AutotoolsDeps(self)
        tc.environment.define("PKG_CONFIG_PATH", self.source_folder)  # FIXME: https://github.com/conan-io/conan/issues/10639 (should work out of the box)
        tc.environment.define("LIBS", "-lpthread")  # FIXME: https://github.com/conan-io/conan/issues/10341 (regression in 1.45, soname arguments are "eaten")
        tc.environment.define("libzstd_LIBS", "-lzstd")  # FIXME: https://github.com/conan-io/conan/issues/10640 (zstd pkg-config includes itself)
        tc.environment.define("zlib_LIBS", "-lz")  # FIXME: https://github.com/conan-io/conan/issues/10651 (command line is polluted by framework arguments)
        tc.environment.define("libcrypto_LIBS", "-lcrypto -ldl -lrt -lpthread")
        tc.environment.define("liblzma_LIBS", "-llzma")
        tc.generate()

    def requirements(self):
        if self.options.with_zstd:
            self.requires('zstd/1.5.2')
        if self.options.with_xz:
            self.requires('xz_utils/5.2.5')
        if self.options.with_zlib:
            self.requires('zlib/1.2.11')
        if self.options.with_openssl:
            self.requires('openssl/3.0.1')

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("kmod is Linux-only!")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],  destination=self._source_subfolder, strip_root=True)

    def build(self):
        tools.save(os.path.join(self._source_subfolder, "libkmod", "docs", "gtk-doc.make"), "")
        self.run("autoreconf -fiv", cwd=self._source_subfolder)
        autotools = Autotools(self)
        autotools.configure(build_script_folder=self._source_subfolder)
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        autotools = Autotools(self)
        autotools.install()
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libkmod")
        self.cpp_info.libs = ["kmod"]
        self.cpp_info.system_libs = ["pthread"]
