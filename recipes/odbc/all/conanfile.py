import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration


class OdbcConan(ConanFile):
    name = 'odbc'
    version = '2.3.7'
    description = 'Package providing unixODBC or Microsoft ODBC'
    url = 'https://github.com/conan-io/conan-center-index'

    license = 'LGPL/GPL'

    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True, False], 'fPIC': [True, False]}
    default_options = {'shared': False, 'fPIC': True}

    _source_subfolder = 'source_subfolder'

    def configure(self):
        del self.settings.compiler.libcxx  # Pure C
        del self.settings.compiler.cppstd
        if self.settings.os == "Windows" and not self.options.shared:
            raise ConanInvalidConfiguration("Only shared library is supported on Windows")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = 'unixODBC-%s' % self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        if self.settings.os == 'Windows':
            return
        env_build = AutoToolsBuildEnvironment(self)
        static_flag = 'no' if self.options.shared else 'yes'
        shared_flag = 'yes' if self.options.shared else 'no'
        args = ['--enable-static=%s' % static_flag,
                '--enable-shared=%s' % shared_flag,
                '--enable-ltdl-install']

        env_build.configure(configure_dir=self._source_subfolder, args=args)
        env_build.make()
        env_build.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "etc"))
        os.remove(os.path.join(self.package_folder, "lib", "pkgconfig", "odbc.pc"))
        os.remove(os.path.join(self.package_folder, "lib", "pkgconfig", "odbccr.pc"))
        os.remove(os.path.join(self.package_folder, "lib", "pkgconfig", "odbcinst.pc"))
        os.remove(os.path.join(self.package_folder, "lib", "libodbc.la"))
        os.remove(os.path.join(self.package_folder, "lib", "libodbccr.la"))
        os.remove(os.path.join(self.package_folder, "lib", "libodbcinst.la"))
        os.remove(os.path.join(self.package_folder, "lib", "libltdl.la"))

    def package(self):
        self.copy('COPYING', src=self._source_subfolder, dst="licenses")
                
    def package_id(self):
        if self.settings.os == "Windows":
            del self.info.settings.arch
            del self.info.settings.build_type
            del self.info.settings.compiler

    def package_info(self):
        self.env_info.path.append(os.path.join(self.package_folder, 'bin'))

        if self.settings.os == 'Windows':
            self.cpp_info.libs = ['odbc32', 'odbccp32']
        else:
            self.cpp_info.libs = ['odbc', 'odbccr', 'odbcinst', 'ltdl']
            if self.settings.os == 'Linux':
                self.cpp_info.libs.append('dl')
            if self.settings.os == 'Macos':
                self.cpp_info.libs.append('iconv')
