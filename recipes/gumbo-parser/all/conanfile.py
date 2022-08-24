from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import os


class GumboParserConan(ConanFile):
    name = "gumbo-parser"
    description = "An HTML5 parsing library in pure C99"
    topics = ("conan", "parser")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/gumbo-parser"
    license = "Apache-2.0"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("This recipe does not support Visual Studio")

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_folder = "gumbo-parser-{0}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            with tools.chdir(self._source_subfolder):
                self.run("./autogen.sh", win_bash=tools.os_info.is_windows)
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            args = []
            if self.options.shared:
                args.extend(['--disable-static', '--enable-shared'])
            else:
                args.extend(['--disable-shared', '--enable-static'])
            self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        os.unlink(os.path.join(self.package_folder, 'lib', 'libgumbo.la'))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "gumbo"
        self.cpp_info.libs = ["gumbo"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
