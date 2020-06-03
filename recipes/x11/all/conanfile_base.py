from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os
import glob
import shutil


class BaseHeaderOnly(ConanFile):
    homepage = "https://www.x.org/wiki/"
    license = "X11"
    url = "https://github.com/bincrafters/conan-x11"
    author = "Bincrafters <bincrafters@gmail.com>"
    settings = "os", "arch", "compiler", "build_type"
    _source_subfolder = "source_subfolder"
    generators = "pkg_config"
    _autotools = None

    def package_info(self):
        if self.name.startswith('lib') and not self.name in ['libfs']:
            self.cpp_info.names['pkg_config'] = self.name[3:]
        self.cpp_info.builddirs.extend([os.path.join("share", "pkgconfig"),
                                        os.path.join("lib", "pkgconfig")])
        self.cpp_info.includedirs = [path for path in self.cpp_info.includedirs if os.path.isdir(path)]
        self.cpp_info.libdirs = [path for path in self.cpp_info.libdirs if os.path.isdir(path)]
        self.cpp_info.libs = tools.collect_libs(self)

    def package_id(self):
        self.info.header_only()

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install(args=["-j1"])
            
        if self.name.startswith('lib') and not self.name in ['libfs']:
            assert(os.path.isfile(os.path.join(self.package_folder, 'lib', 'pkgconfig', self.name[3:] + '.pc')))

    @property
    def _configure_args(self):
        return []

    def _configure_autotools(self):
        if not self._autotools:
            args = ["--disable-dependency-tracking"]
            args.extend(self._configure_args)
            self._autotools = AutoToolsBuildEnvironment(self)
            self._autotools.configure(args=args, pkg_config_paths=self.build_folder)
        return self._autotools

    def build(self):
        for package in self.deps_cpp_info.deps:
            lib_path = self.deps_cpp_info[package].rootpath
            for dirpath, _, filenames in os.walk(lib_path):
                for filename in filenames:
                    if filename.endswith('.pc'):
                        shutil.copyfile(os.path.join(dirpath, filename), filename)
                        tools.replace_prefix_in_pc_file(filename, lib_path)

        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.make()


class BaseLib(BaseHeaderOnly):
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def configure(self):
        super(BaseLib, self).configure()
        if self.settings.os == "Windows":
            del self.options.fPIC

    @property
    def _configure_args(self):
        if self.options.shared:
            return ["--disable-static", "--enable-shared"]
        else:
            return ["--disable-shared", "--enable-static"]

    def package(self):
        super(BaseLib, self).package()
        libdir = os.path.join(self.package_folder, "lib")
        if os.path.isdir(libdir):
            with tools.chdir(libdir):
                # libtool *.la files have hard-coded paths
                for filename in glob.glob("*.la"):
                    os.unlink(filename)
                # libXaw has broken symlinks
                if not self.options.shared:
                    for filename in glob.glob("*.dylib"):
                        os.unlink(filename)
                    for filename in glob.glob("*.so"):
                        os.unlink(filename)
                    for filename in glob.glob("*.so.*"):
                        os.unlink(filename)

    def package_id(self):
        pass
