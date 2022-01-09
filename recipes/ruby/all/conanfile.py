import os
import re
from io import StringIO

from conan import ConanFile
from conan.tools.files import apply_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conans import tools

required_conan_version = ">=1.43.0"


class RubyConan(ConanFile):
    name = "ruby"
    description = "The Ruby Programming Language"
    license = "Ruby"
    topics = ("ruby", "c", "language", "object-oriented", "ruby-language")
    homepage = "https://www.ruby-lang.org"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "patches/**"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": True
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("zlib/1.2.11")
        self.requires("gmp/6.2.1")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1m")

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def generate(self):
        td = AutotoolsDeps(self)
        # remove non-existing frameworks dirs, otherwise clang complains
        for m in re.finditer("-F (\S+)", td.vars().get("LDFLAGS")):
            if not os.path.exists(m[1]):
                td.environment.remove("LDFLAGS", "-F {}".format(m[1]))
        td.generate()

        tc = AutotoolsToolchain(self)
        tc.default_configure_install_args = True
        tc.configure_args = ["--disable-install-doc"]
        tc.generate()

    def build(self):
        apply_conandata_patches(self)

        at = Autotools(self)
        at.configure(build_script_folder=self._source_subfolder)
        at.make()

    def package(self):
        for file in ["COPYING", "BSDL"]:
            self.copy(file, dst="licenses", src=self._source_subfolder)

        at = Autotools(self)
        at.install()

        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        binpath = os.path.join(self.package_folder, "bin")
        self.output.info("Adding to PATH: {}".format(binpath))
        self.env_info.PATH.append(binpath)

        version = tools.Version(self.version)
        rubylib = self.cpp_info.components["rubylib"]
        arch_buf = StringIO()
        self.run([os.path.join(self.package_folder, 'bin', 'ruby'), "-e", "require 'mkmf'; puts(CONFIG['arch'])"], output=arch_buf)
        rubylib.includedirs = [
            os.path.join(self.package_folder, "include", "ruby-{}".format(version)),
            os.path.join(self.package_folder, "include", "ruby-{}".format(version), arch_buf.getvalue().strip())
        ]
        rubylib.libs = tools.collect_libs(self)
        rubylib.requires.extend(["zlib::zlib", "gmp::gmp"])
        if self.options.with_openssl:
            rubylib.requires.append("openssl::openssl")
        if self.settings.os in ("FreeBSD", "Linux"):
            rubylib.system_libs = ["dl", "pthread", "rt", "m", "crypt"]
        elif self.settings.os == "Windows":
            rubylib.system_libs = ["shell32", "ws2_32", "iphlpapi", "imagehlp", "shlwapi", "bcrypt"]
        if str(self.settings.compiler) in ("clang", "apple-clang"):
            rubylib.cflags = ["-fdeclspec"]
            rubylib.cxxflags = ["-fdeclspec"]
        if tools.is_apple_os(self.settings.os):
            rubylib.frameworks = ["CoreFoundation"]

        self.cpp_info.filenames["cmake_find_package"] = "Ruby"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Ruby"
        self.cpp_info.set_property("cmake_file_name", "Ruby")

        self.cpp_info.names["cmake_find_package"] = "Ruby"
        self.cpp_info.names["cmake_find_package_multi"] = "Ruby"
        self.cpp_info.set_property("cmake_target_name", "Ruby::Ruby")
        self.cpp_info.set_property("pkg_config_aliases", ["ruby-{}.{}".format(version.major, version.minor)])
