from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.33.0"


class OpenMPIConan(ConanFile):
    name = "openmpi"
    homepage = "https://www.open-mpi.org"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("mpi", "openmpi")
    description = "A High Performance Message Passing Library"
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "fortran": ["yes", "mpifh", "usempi", "usempi80", "no"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "fortran": "no",
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        # FIXME : self.requires("libevent/2.1.12") - try to use libevent from conan
        self.requires("zlib/1.2.12")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("OpenMPI doesn't support Windows")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--disable-wrapper-rpath",
            "--disable-wrapper-runpath",
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--with-pic={}".format(yes_no(self.options.get_safe("fPIC", True))),
            "--enable-mpi-fortran={}".format(str(self.options.fortran)),
            "--with-zlib={}".format(self.deps_cpp_info["zlib"].rootpath),
            "--with-zlib-libdir={}".format(self.deps_cpp_info["zlib"].lib_paths[0]),
            "--datarootdir=${prefix}/res",
        ]
        if self.settings.build_type == "Debug":
            args.append("--enable-debug")
        autotools.configure(args=args)
        return autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "etc"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.libs = ["mpi", "open-rte", "open-pal"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl", "pthread", "rt", "util"]

        self.output.info("Creating MPI_HOME environment variable: {}".format(self.package_folder))
        self.env_info.MPI_HOME = self.package_folder
        self.output.info("Creating OPAL_PREFIX environment variable: {}".format(self.package_folder))
        self.env_info.OPAL_PREFIX = self.package_folder
        mpi_bin = os.path.join(self.package_folder, "bin")
        self.output.info("Creating MPI_BIN environment variable: {}".format(mpi_bin))
        self.env_info.MPI_BIN = mpi_bin
        self.output.info("Appending PATH environment variable: {}".format(mpi_bin))
        self.env_info.PATH.append(mpi_bin)
