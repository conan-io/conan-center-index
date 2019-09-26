import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration


class OdbcConan(ConanFile):
    name = 'odbc'
    description = 'Package providing unixODBC'
    url = 'https://github.com/conan-io/conan-center-index'
    homepage = "http://www.unixodbc.org"
    author = "Bincrafters <bincrafters@gmail>"
    license = ('LGPL-2.1', 'GPL-2.1')

    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True, False], 'fPIC': [True, False]}
    default_options = {'shared': False, 'fPIC': True}
    topics = ('odbc', 'database', 'dbms', 'data-access')

    _source_subfolder = 'source_subfolder'

    def configure(self):
        del self.settings.compiler.libcxx  # Pure C
        del self.settings.compiler.cppstd
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows not supported yet. Please, open an issue if you need such support")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = 'unixODBC-%s' % self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
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
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        os.remove(os.path.join(self.package_folder, "lib", "libodbc.la"))
        os.remove(os.path.join(self.package_folder, "lib", "libodbccr.la"))
        os.remove(os.path.join(self.package_folder, "lib", "libodbcinst.la"))
        os.remove(os.path.join(self.package_folder, "lib", "libltdl.la"))

    def package(self):
        self.copy('COPYING', src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.env_info.path.append(os.path.join(self.package_folder, 'bin'))

        self.cpp_info.libs = ['odbc', 'odbccr', 'odbcinst', 'ltdl']
        if self.settings.os == 'Linux':
            self.cpp_info.libs.append('dl')
        if self.settings.os == 'Macos':
            self.cpp_info.libs.append('iconv')
