from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os
import glob

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
               "without_video": [True, False],
               "without_imagemagick": [True, False],
               "without_gtk": [True, False],
               "without_qt": [True, False],
               "without_python_bindings": [True, False],
               "with_x": [True, False],
               "without_xshm": [True, False],
               "without_xv": [True, False],
               "without_jpeg": [True, False],
               "disable_pthread": [True, False],}
    default_options = {'shared': False,
                       'fPIC': True,
                       'without_video': True,
                       'without_imagemagick': True,
                       'without_gtk': True,
                       'without_qt': True,
                       'without_python_bindings': True,
                       'with_x': False,
                       'without_xshm': False,
                       'without_xv': False,
                       'without_jpeg': False,
                       'disable_pthread': False,
                       }

    _env_build = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _configure_autotools(self):
        if not self._env_build:
            self._env_build = AutoToolsBuildEnvironment(self)
            env_args = []
            if self.options.without_video:
                env_args.extend(["--disable-video"])
            if self.options.without_imagemagick:
                env_args.extend(["--without-imagemagick"])
            if self.options.with_gtk:
                env_args.extend(["--with-gtk"])
            if self.options.without_qt:
                env_args.extend(["--without-qt"])
            if self.options.without_python_bindings:
                env_args.extend(["--without-python"])
            if self.options.without_x:
                env_args.extend(["--without-x"])
            if self.options.without_xshm:
                env_args.extend(["--without-xshm"])
            if self.options.without_xv:
                env_args.extend(["--without-xv"])
            if self.options.disable_pthread:
                env_args.extend(["--disable-pthread"])
            if self.options.without_jpeg:
                env_args.extend(["--without-jpeg"])
            if self.options.shared:
                env_args.extend(["--enable-shared", "--disable-static"])
            else:
                env_args.extend(["--enable-static", "--disable-shared"])
            self._env_build.configure(args=env_args, configure_dir=self._source_subfolder)
        return self._env_build

    def configure(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Zbar can't be built on Windows")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
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
        if self.settings.os == "Linux" and not self.options.disable_pthread:
            self.cpp_info.system_libs = ["pthread"]