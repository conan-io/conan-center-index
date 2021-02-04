from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os


class OpenMPIConan(ConanFile):
    name = "openmpi"
    homepage = "https://www.open-mpi.org"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "mpi", "openmpi")
    description = "A High Performance Message Passing Library"
    license = "https://www.open-mpi.org/community/license.php"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "fortran": ['yes', 'mpifh', 'usempi', 'usempi80', 'no']}
    default_options = {'shared': False, 'fPIC': True, 'fortran': 'no'}
    _source_subfolder = "sources"

    def config(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("OpenMPI doesn't support Windows")

    def requirements(self):
        self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        with tools.chdir(self._source_subfolder):
            env_build = AutoToolsBuildEnvironment(self)
            env_build.fpic = self.options.fPIC
            args = ['--disable-wrapper-rpath', '--disable-wrapper-runpath']
            if self.settings.build_type == 'Debug':
                args.append('--enable-debug')
            if self.options.shared:
                args.extend(['--enable-shared', '--disable-static'])
            else:
                args.extend(['--enable-static', '--disable-shared'])
            args.append('--with-pic' if self.options.fPIC else '--without-pic')
            args.append('--enable-mpi-fortran=%s' % str(self.options.fortran))
            args.append('--with-zlib=%s' % self.deps_cpp_info['zlib'].rootpath)
            args.append('--with-zlib-libdir=%s' % self.deps_cpp_info['zlib'].lib_paths[0])
            args.append('--datarootdir=${prefix}/res')
            env_build.configure(args=args)
            env_build.make()
            env_build.install()

    def package(self):
        self.copy(pattern="LICENSE", src='sources', dst='licenses')

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "etc"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.libs = ['mpi', 'open-rte', 'open-pal']
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(['dl', 'pthread', 'rt', 'util'])
        self.env_info.MPI_HOME = self.package_folder
        self.env_info.OPAL_PREFIX = self.package_folder
        mpi_bin = os.path.join(self.package_folder, 'bin')
        self.env_info.MPI_BIN = mpi_bin
        self.env_info.PATH.append(mpi_bin)
