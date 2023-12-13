import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import unix_path

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
        "cxx": [True, False],
        "cxx_exceptions": [True, False],
        "with_verbs": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "fortran": "no",
        "cxx": False,
        "cxx_exceptions": False,
        "with_verbs": False,  # TODO: can be enabled once rdma-core is available
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.cxx:
            self.settings.rm_safe("compiler.libcxx")
            self.settings.rm_safe("compiler.cppstd")
        if is_apple_os(self):
            # Unavailable due to dependency on libnl
            del self.options.with_verbs

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        if not self.info.options.cxx:
            del self.info.options.cxx_exceptions

    def requirements(self):
        self.requires("hwloc/2.9.3")
        self.requires("libevent/2.1.12")
        self.requires("libtool/2.4.7")
        self.requires("zlib/[>=1.2.11 <2]")
        if not is_apple_os(self):
            self.requires("libnl/3.8.0")
        if self.options.get_safe('with_verbs'):
            self.requires("rdma-core/49.0")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("OpenMPI doesn't support Windows")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        def root(pkg):
            return unix_path(self, self.dependencies[pkg].package_folder)

        def yes_no(v):
            return "yes" if v else "no"

        tc = AutotoolsToolchain(self)
        tc.configure_args += [
            f"--enable-mpi-fortran={self.options.fortran}",
            f"--enable-mpi-cxx={yes_no(self.options.cxx)}",
            f"--enable-cxx-exceptions={yes_no(self.options.get_safe('cxx_exceptions'))}",
            f"--with-hwloc={root('hwloc')}",
            f"--with-libevent={root('libevent')}",
            f"--with-libltdl={root('libtool')}",
            f"--with-libnl={root('libnl') if not is_apple_os(self) else 'no'}",
            f"--with-verbs={root('rdma-core') if self.options.get_safe('with_verbs') else 'no'}",
            f"--with-zlib={root('zlib')}",
            "--enable-ipv6",
            "--with-sge",  # SGE or Grid Engine support
            "--disable-wrapper-rpath",
            "--disable-wrapper-runpath",
            "--exec-prefix=/",
            "--datarootdir=${prefix}/res",
            # Disable other external libraries explicitly
            "--with-alps=no",  # ALPS
            "--with-cuda=no",  # CUDA
            "--with-fca=no",  # FCA
            "--with-gpfs=no",  # Gpfs
            "--with-hcoll=no",  # hcoll
            "--with-ime=no",  # IME
            "--with-lsf=no",  # LSF
            "--with-lustre=no",  # Lustre
            "--with-memkind=no",  # memkind
            "--with-moab=no",  # Moab
            "--with-mxm=no",  # Mellanox MXM
            "--with-ofi=no",  # libfabric, TODO: enable once libfabric is available
            "--with-pmi=no",  # PMI
            "--with-pmix=internal",  # PMIx
            "--with-portals4=no",  # Portals4
            "--with-psm2=no",  # PSM2
            "--with-psm=no",  # PSM
            "--with-pvfs2=no",  # Pvfs2
            "--with-treematch=no",  # TreeMatch
            "--with-ucx=no",  # UCX
            "--with-valgrind=no",  # Valgrind
            "--with-x=no",  # X11
            "--with-xpmem=no",  # XPMEM
        ]
        if is_apple_os(self):
            # macOS has no libnl
            tc.configure_args.append("--enable-mca-no-build=reachable-netlink")
        tc.generate()

        # TODO: might want to enable reproducible builds by setting
        #  $SOURCE_DATE_EPOCH, $USER and $HOSTNAME

        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
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

        bin_folder = os.path.join(self.package_folder, "bin")
        self.runenv.define_path("MPI_BIN", bin_folder)
        self.runenv.define_path("MPI_HOME", self.package_folder)
        self.runenv.define_path("OPAL_PREFIX", self.package_folder)
        self.runenv.define_path("OPAL_EXEC_PREFIX", self.package_folder)
        self.runenv.define_path("OPAL_DATAROOTDIR", os.path.join(self.package_folder, "res"))

        # TODO: Legacy, to be removed on Conan 2.0
        self.env_info.PATH.append(bin_folder)
        self.env_info.MPI_BIN = bin_folder
        self.env_info.MPI_HOME = self.package_folder
        self.env_info.OPAL_PREFIX = self.package_folder
        self.env_info.OPAL_EXEC_PREFIX = self.package_folder
        self.env_info.OPAL_DATAROOTDIR = os.path.join(self.package_folder, "res")
