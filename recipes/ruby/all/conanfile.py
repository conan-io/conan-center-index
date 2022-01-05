import os

from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conans import tools

required_conan_version = ">=1.43.0"


class RubyConan(ConanFile):
    name = "ruby"
    description = "The Ruby Programming Language"
    license = "Ruby"
    topics = ("ruby", "c", "language", "object-oriented", "ruby-language")
    homepage = "https://www.ruby-lang.org"
    url = "https://github.com/conan-io/conan-center-index"
    generators = "AutotoolsToolchain"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("zlib/1.2.11")

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
        tc = AutotoolsToolchain(self)
        tc.default_configure_install_args = True
        if self.settings.os != "Linux":
            zlib = self.deps_cpp_info["zlib"]
            tc.cflags = ["-I{}".format(os.path.join(zlib.rootpath, dir)) for dir in zlib.includedirs]
            tc.ldflags = ["-L{}".format(os.path.join(zlib.rootpath, dir)) for dir in zlib.libdirs]
        tc.generate()

    def build(self):
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
        rubylib.includedirs = [
            os.path.join(self.package_folder, "include", "ruby-{}".format(version)),
            os.path.join(self.package_folder, "include", "ruby-{}".format(version), "{}-{}".format(self.settings.arch, str(self.settings.os).lower()))
        ]
        rubylib.libs = tools.collect_libs(self)
        rubylib.requires.append("zlib::zlib")
        if self.settings.os in ("FreeBSD", "Linux"):
            rubylib.system_libs = ["dl", "pthread", "rt", "m", "gmp", "crypt"]
        elif self.settings.os == "Windows":
            rubylib.system_libs = ["shell32", "ws2_32", "iphlpapi", "imagehlp", "shlwapi", "bcrypt"]

        rubylib.filenames["cmake_find_package"] = "Ruby"
        rubylib.filenames["cmake_find_package_multi"] = "Ruby"
        rubylib.set_property("cmake_file_name", "Ruby")

        rubylib.names["cmake_find_package"] = "Ruby"
        rubylib.names["cmake_find_package_multi"] = "Ruby"
        rubylib.set_property("cmake_target_name", "Ruby::Ruby")
        rubylib.set_property("pkg_config_aliases", ["ruby-{}.{}".format(version.major, version.minor)])
