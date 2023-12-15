import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.files import copy, get, rm, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsToolchain
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
        "external_hwloc": [True, False],
        "with_verbs": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "fortran": "no",
        "cxx": False,
        "cxx_exceptions": False,
        "external_hwloc": True,
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
        # OpenMPI public headers don't include anything besides stddef.h.
        # transitive_headers=True is not needed for any dependencies.
        self.requires("zlib/[>=1.2.11 <2]")
        if not is_apple_os(self):
            self.requires("libnl/3.8.0")
        if self.options.external_hwloc:
            self.requires("hwloc/2.9.3")
        else:
            self.requires("libpciaccess/0.17")
            self.requires("libudev/system")
        if self.options.get_safe("with_verbs"):
            self.requires("rdma-core/49.0")

    def validate(self):
        if self.settings.os == "Windows":
            # Requires Cygwin or WSL
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
            f"--with-hwloc={root('hwloc') if self.options.external_hwloc else 'internal'}",
            f"--with-libnl={root('libnl') if not is_apple_os(self) else 'no'}",
            f"--with-verbs={root('rdma-core') if self.options.get_safe('with_verbs') else 'no'}",
            f"--with-zlib={root('zlib')}",
            "--with-pic" if self.options.get_safe("fPIC", True) else "--without-pic",
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
        # libtool's libltdl is not really needed, OpenMPI provides its own equivalent.
        # Not adding it as it fails to be detected by ./configure in some cases.
        # https://github.com/open-mpi/ompi/blob/v4.1.6/opal/mca/dl/dl.h#L20-L25
        tc.configure_args.append("--with-libltdl=no")
        # OpenMPI expects a single libevent.* library file,
        # ./configure with a external libevent fails.
        tc.configure_args.append("--with-libevent=internal")
        tc.generate()

        # TODO: might want to enable reproducible builds by setting
        #  $SOURCE_DATE_EPOCH, $USER and $HOSTNAME

    def _patch_sources(self):
        # Not needed and fails with v5.0 due to additional Python dependencies
        save(self, os.path.join(self.source_folder, "docs", "Makefile.in"), "all:\ninstall:\n")

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "etc"))
        rmdir(self, os.path.join(self.package_folder, "res", "man"))
        rm(self, "*.la", self.package_folder, recursive=True)

    def package_info(self):
        # Based on https://cmake.org/cmake/help/latest/module/FindMPI.html#variables-for-using-mpi
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "MPI")
        self.cpp_info.set_property("pkg_config_name", "_ompi-do-not-use")
        # TODO: export a .cmake module to correctly set all variables set by CMake's FindMPI.cmake

        requires = ["zlib::zlib"]
        if not is_apple_os(self):
            requires.append("libnl::libnl")
        if self.options.external_hwloc:
            requires.append("hwloc::hwloc")
        else:
            requires.append("libpciaccess::libpciaccess")
            requires.append("libudev::system")
        if self.options.get_safe("with_verbs"):
            requires.append("rdma-core::libibverbs")

        # The components are modelled based on OpenMPI's pkg-config files

        # Run-time environment library
        self.cpp_info.components["orte"].libs = ["open-rte", "open-pal"]
        self.cpp_info.components["orte"].includedirs.append(os.path.join("include", "openmpi"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["orte"].system_libs = ["dl", "pthread", "rt", "util"]
        self.cpp_info.components["orte"].cflags = ["-pthread"]
        if self.options.cxx_exceptions:
            self.cpp_info.components["orte"].cflags.append("-fexceptions")
        self.cpp_info.components["orte"].requires = requires

        self.cpp_info.components["ompi"].libs = ["mpi"]
        self.cpp_info.components["ompi"].requires = ["orte"]

        self.cpp_info.components["ompi-c"].set_property("cmake_target_name", "MPI::MPI_C")
        self.cpp_info.components["ompi-c"].requires = ["ompi"]

        self.cpp_info.components["ompitrace"].libs = ["ompitrace"]
        self.cpp_info.components["ompitrace"].requires = ["ompi"]

        if self.options.cxx:
            self.cpp_info.components["ompi-cxx"].set_property("cmake_target_name", "MPI::MPI_CXX")
            self.cpp_info.components["ompi-cxx"].libs = ["mpi_cxx"]
            self.cpp_info.components["ompi-cxx"].requires = ["mpi"]

        if self.options.fortran != "no":
            self.cpp_info.components["ompi-fort"].set_property("cmake_target_name", "MPI::MPI_Fortran")
            self.cpp_info.components["ompi-fort"].libs = ["mpi_mpifh"]
            self.cpp_info.components["ompi-fort"].requires = ["mpi"]
            # Aliases
            self.cpp_info.components["ompi-f77"].requires = ["ompi-fort"]
            self.cpp_info.components["ompi-f90"].requires = ["ompi-fort"]

        bin_folder = os.path.join(self.package_folder, "bin")
        # Prepend to PATH to avoid a conflict with system MPI
        self.runenv_info.prepend_path("PATH", bin_folder)
        self.runenv_info.define_path("MPI_BIN", bin_folder)
        self.runenv_info.define_path("MPI_HOME", self.package_folder)
        self.runenv_info.define_path("OPAL_PREFIX", self.package_folder)
        self.runenv_info.define_path("OPAL_EXEC_PREFIX", self.package_folder)
        self.runenv_info.define_path("OPAL_LIBDIR", os.path.join(self.package_folder, "lib"))
        self.runenv_info.define_path("OPAL_DATADIR", os.path.join(self.package_folder, "res"))
        self.runenv_info.define_path("OPAL_DATAROOTDIR", os.path.join(self.package_folder, "res"))

        # TODO: Legacy, to be removed on Conan 2.0
        self.env_info.PATH.append(bin_folder)
        self.env_info.MPI_BIN = bin_folder
        self.env_info.MPI_HOME = self.package_folder
        self.env_info.OPAL_PREFIX = self.package_folder
        self.env_info.OPAL_EXEC_PREFIX = self.package_folder
        self.env_info.OPAL_LIBDIR = os.path.join(self.package_folder, "lib")
        self.env_info.OPAL_DATADIR = os.path.join(self.package_folder, "res")
        self.env_info.OPAL_DATAROOTDIR = os.path.join(self.package_folder, "res")

        self.cpp_info.names["cmake_find_package"] = "MPI"
        self.cpp_info.names["cmake_find_package_multi"] = "MPI"
        self.cpp_info.components["ompi-c"].names["cmake_find_package"] = "MPI_C"
        if self.options.cxx:
            self.cpp_info.components["ompi-cxx"].names["cmake_find_package"] = "MPI_CXX"
        if self.options.fortran != "no":
            self.cpp_info.components["ompi-fort"].names["cmake_find_package"] = "MPI_Fortran"
