from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os
import glob
import shutil

class zbarConan(ConanFile):
    name = "zbar"
    license = "LGPL-2.1-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://zbar.sourceforge.net/"
    topics = ("conan", "zbar", "bar codes")
    description = "ZBar is an open source software suite for reading bar codes\
                   from various sources, such as video streams, image files and raw intensity sensors"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_video": [True, False],
               "with_imagemagick": [True, False],
               "with_gtk": [True, False],
               "with_qt": [True, False],
               "with_python_bindings": [True, False],
               "with_x": [True, False],
               "with_xshm": [True, False],
               "with_xv": [True, False],
               "with_jpeg": [True, False],
               "enable_pthread": [True, False],}
    default_options = {'shared': False,
                       'fPIC': True,
                       'with_video': False,
                       'with_imagemagick': False,
                       'with_gtk': False,
                       'with_qt': False,
                       'with_python_bindings': False,
                       'with_x': False,
                       'with_xshm': False,
                       'with_xv': False,
                       'with_jpeg': False,
                       'enable_pthread': True,
                       }

    _env_build = None

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", None) or self.deps_user_info

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _configure_autotools(self):
        if not self._env_build:
            self._env_build = AutoToolsBuildEnvironment(self)
            env_args = [
                "--enable-video" if self.options.with_video else "--disable-video",
                "--with-imagemagick" if self.options.with_imagemagick else "--without-imagemagick",
                "--with-gtk" if self.options.with_gtk else "--without-gtk",
                "--with-qt" if self.options.with_qt else "--without-qt",
                "--with-python" if self.options.with_python_bindings else "--without-python",
                "--with-x" if self.options.with_x else "--without-x",
                "--with-xshm" if self.options.with_xshm else "--without-xshm",
                "--with-xv" if self.options.with_xv else "--without-xv",
                "--with-jpeg" if self.options.with_jpeg else "--without-jpeg",
                "--enable-pthread" if self.options.enable_pthread else "--disable-pthread",
                "--enable-shared" if self.options.shared else "--disable-shared",
                "--enable-static" if not self.options.shared else "--disable-static",
            ]
            if self.settings.os == "Macos" and self.settings.arch == "armv8":
               # ./libtool: eval: line 961: syntax error near unexpected token `|'
                env_args.append("NM=nm")
            self._env_build.configure(args=env_args, configure_dir=self._source_subfolder)
        return self._env_build

    def requirements(self):
        if self.options.with_jpeg:
            self.requires("libjpeg/9d")

    def build_requirements(self):
        self.build_requires("gnu-config/cci.20201022")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Zbar can't be built on Windows")
        if tools.is_apple_os(self.settings.os) and not self.options.shared:
            raise ConanInvalidConfiguration("Zbar can't be built static on macOS")
        if self.options.with_imagemagick:   #TODO add when available
            self.output.warn("There is no imagemagick package available on Conan (yet). This recipe will use the one present on the system (if available).")
        if self.options.with_gtk:           #TODO add when available
            self.output.warn("There is no gtk package available on Conan (yet). This recipe will use the one present on the system (if available).")
        if self.options.with_qt:            #TODO add when available
            self.output.warn("There is no qt package available on Conan (yet). This recipe will use the one present on the system (if available).")
        if self.options.with_xv:            #TODO add when available
            self.output.warn("There is no Xvideo package available on Conan (yet). This recipe will use the one present on the system (if available).")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self._source_subfolder, "config", "config.sub"))
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self._source_subfolder, "config", "config.guess"))

        env_build = self._configure_autotools()
        env_build.make()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        env_build = self._configure_autotools()
        env_build.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        for dot_la_files in glob.iglob(os.path.join(self.package_folder, "lib", '*.la')):
            os.remove(dot_la_files)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux" and self.options.enable_pthread:
            self.cpp_info.system_libs = ["pthread"]
        if tools.is_apple_os(self.settings.os):
            self.cpp_info.system_libs = ["iconv"]

