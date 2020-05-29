import os
from glob import glob
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration

class LibvaConan(ConanFile):
    name = "libva"
    description = "Libva is an implementation for VA-API (VIdeo Acceleration API)"
    url = "https://github.com/trassir/conan-center-index"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = [ "patches/*.patch" ]
    generators = "pkg_config"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "x11": [True, False],
        "drm": [True, False],
        "wayland": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "x11": True,
        "drm": False,
        "wayland": False,
    }
    _autotools = None
    _source_subfolder = "source_subfolder"

    def configure(self):
        if not tools.os_info.is_linux:
            raise NotImplementedError()

    def requirements(self):
        # despite drm being an option, the library is required unconditionally
        self.requires("libdrm/2.4.100")
        if self.options.x11:
            self.requires("libx11/1.6.8")
            self.requires("libxext/1.3.4")
            self.requires("libxfixes/5.0.3")
        if self.options.wayland:
            raise NotImplementedError()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        # yes, 1.5.1 named as libva-libva-1.5.1
        extracted_dir = self.name + "-" + self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            if not os.path.isdir('m4'):
                os.makedirs('m4')
            self.run('autoreconf -v --install')

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        def enable(arg, attr=None):
            attr = attr or arg
            return '--enable-'+arg if self.options.__getattr__(attr) else '--disable-'+arg
        args = [
            enable("x11"),
            enable("wayland"),
            enable("drm"),
            enable("shared"),
        ]
        args.append('--disable-static' if self.options.shared else '--enable-static')
        args.append('--disable-dummy-driver')
        args.append('--with-pic' if self.options.fPIC else '--without-pic')
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        self._configure_autotools().make(args=["-j%d" % tools.cpu_count()])

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        self._configure_autotools().install()
        # drop pc and bin files
        tools.rmdir(os.path.join(self.package_folder, 'bin'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        # drop la files
        for la_file in glob(os.path.join(self.package_folder, "lib", '*.la')):
            os.unlink(la_file)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libs = ['va-tpi', 'va']
        if self.options.x11:
            self.cpp_info.libs.append('va-x11')
        if self.options.drm:
            self.cpp_info.libs.append('va-drm')
