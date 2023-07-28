import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import chdir, copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"


class OpenMPIConan(ConanFile):
    name = "openmpi"
    description = "A High Performance Message Passing Library"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.open-mpi.org"
    topics = ("mpi", "openmpi")

    package_type = "library"
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("OpenMPI doesn't support Windows")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libevent/2.1.12")
        self.requires("zlib/1.2.13")
        self.requires("hwloc/2.9.2")
        self.requires("rdma-core/47.0")
        self.requires("libnl/3.7.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()
        args = ["--disable-wrapper-rpath", "--disable-wrapper-runpath"]
        if self.settings.build_type == "Debug":
            args.append("--enable-debug")
        args.append("--enable-mpi-fortran={}".format(self.options.fortran))
        args.append("--with-libevent=external")
        args.append("--with-hwloc=external")
        # TODO: add --enable-mpi-cxx
        args.append("--exec-prefix=/")
        args.append("--datarootdir=${prefix}/res")
        tc.configure_args += args
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "etc"))
        rmdir(self, os.path.join(self.package_folder, "res", "man"))
        rm(self, "*.la", self.package_folder, recursive=True)

    def package_info(self):
        # Based on https://cmake.org/cmake/help/latest/module/FindMPI.html#variables-for-using-mpi
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "MPI")
        self.cpp_info.set_property("cmake_target_name", "MPI::MPI")
        self.cpp_info.set_property("cmake_target_aliases", ["MPI::MPI_C", "MPI::MPI_CXX"])
        # TODO: export a .cmake module to correctly set all variables set by CMake's FindMPI.cmake

        self.cpp_info.resdirs = ["res"]
        self.cpp_info.libs = ["mpi", "open-rte", "open-pal"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl", "pthread", "rt", "util"]

        mpi_bin = os.path.join(self.package_folder, "bin")
        self.runenv.define_path("MPI_HOME", self.package_folder)
        self.runenv.define_path("MPI_BIN", mpi_bin)

        # TODO: Legacy, to be removed on Conan 2.0
        self.output.info(f"Creating MPI_HOME environment variable: {self.package_folder}")
        self.env_info.MPI_HOME = self.package_folder
        self.output.info(f"Creating OPAL_PREFIX environment variable: {self.package_folder}")
        self.env_info.OPAL_PREFIX = self.package_folder
        self.output.info(f"Creating MPI_BIN environment variable: {mpi_bin}")
        self.env_info.MPI_BIN = mpi_bin
        self.output.info(f"Appending PATH environment variable: {mpi_bin}")
        self.env_info.PATH.append(mpi_bin)
