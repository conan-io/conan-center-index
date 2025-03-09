import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.env import VirtualRunEnv
from conan.tools.files import copy, get, rm, rmdir, save, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsDeps, GnuToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import unix_path
from conan.tools.scm import Version

required_conan_version = ">=2.3.0"


class OpenMPIConan(ConanFile):
    name = "openmpi"
    description = "A High Performance Message Passing Library"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.open-mpi.org"
    topics = ("mpi", "openmpi")
    provides = "mpi"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "fortran": ["yes", "mpifh", "usempi", "usempi80", "no"],
        "with_libfabric": [True, False],
        # Added in v5.0
        "with_curl": [True, False],
        "with_jansson": [True, False],
        # Removed in v5.0
        "enable_cxx": [True, False],
        "enable_cxx_exceptions": [True, False],
        "with_verbs": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "fortran": "no",
        "with_libfabric": False,
        # Added in v5.0
        "with_curl": False,
        "with_jansson": False,
        # Removed in v5.0
        "enable_cxx": False,
        "enable_cxx_exceptions": False,
        "with_verbs": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) >= "5.0":
            # No longer used in v5.0
            del self.options.with_verbs
            # The C++ bindings were deprecated in v2.2, removed from the standard in v3.0
            # and were removed from the implementation in v5.0.
            del self.options.enable_cxx
            del self.options.enable_cxx_exceptions
        else:
            del self.options.with_curl
            del self.options.with_jansson

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.get_safe("enable_cxx"):
            self.settings.rm_safe("compiler.libcxx")
            self.settings.rm_safe("compiler.cppstd")
            self.options.rm_safe("enable_cxx_exceptions")
        if is_apple_os(self):
            # Unavailable due to dependency on libnl
            self.options.rm_safe("with_verbs")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # OpenMPI public headers don't include anything besides stddef.h.
        # transitive_headers=True is not needed for any dependencies.
        self.requires("hwloc/2.11.1")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("libevent/2.1.12")
        if self.settings.os == "Linux":
            self.requires("libnl/3.8.0")
        if self.options.get_safe("with_curl"):
            self.requires("libcurl/[>=7.78 <9]")
        if self.options.get_safe("with_jansson"):
            # v2.14 is not compatible as of v5.0.5
            self.requires("jansson/2.13.1")
        if self.options.get_safe("with_libfabric"):
            self.requires("libfabric/1.21.0")
        if self.options.get_safe("with_verbs"):
            self.requires("rdma-core/52.0")

    def validate(self):
        if self.settings.os == "Windows":
            # Requires Cygwin or WSL
            raise ConanInvalidConfiguration("OpenMPI doesn't support Windows")

        if self.version == "4.1.0" and is_apple_os(self) and self.settings.arch == "armv8":
            # INFO: https://github.com/open-mpi/ompi/issues/8410
            raise ConanInvalidConfiguration(f"{self.ref} is not supported in Mac M1. Use a newer version.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        def root(pkg):
            return unix_path(self, self.dependencies[pkg].package_folder)

        def yes_no(v):
            return "yes" if v else "no"

        tc = GnuToolchain(self)
        tc.configure_args["--with-pic"] = self.options.get_safe("fPIC")
        tc.configure_args["--enable-mpi-fortran"] = self.options.fortran
        tc.configure_args["--with-hwloc"] = root("hwloc")
        tc.configure_args["--with-libevent"] = root("libevent")
        tc.configure_args["--with-libnl"] = root("libnl") if not is_apple_os(self) else "no"
        tc.configure_args["--with-ofi"] = root("libfabric") if self.options.get_safe("with_libfabric") else "no"
        tc.configure_args["--with-zlib"] = root("zlib")
        tc.configure_args["--with-pmix"] = "internal"
        tc.configure_args["--enable-wrapper-rpath"] = "no"
        tc.configure_args["--enable-wrapper-runpath"] = "no"
        tc.configure_args["--exec-prefix"] = "/"
        tc.configure_args["--datarootdir"] = "${prefix}/res"
        # Disable other external libraries explicitly
        tc.configure_args["--with-alps"] = "no"  # ALPS
        tc.configure_args["--with-cuda"] = "no"  # CUDA
        tc.configure_args["--with-gpfs"] = "no"  # Gpfs
        tc.configure_args["--with-hcoll"] = "no"  # hcoll
        tc.configure_args["--with-ime"] = "no"  # IME
        tc.configure_args["--with-lsf"] = "no"  # LSF
        tc.configure_args["--with-lustre"] = "no"  # Lustre
        tc.configure_args["--with-memkind"] = "no"  # memkind
        tc.configure_args["--with-portals4"] = "no"  # Portals4
        tc.configure_args["--with-psm2"] = "no"  # PSM2
        tc.configure_args["--with-pvfs2"] = "no"  # Pvfs2
        tc.configure_args["--with-treematch"] = "no"  # TreeMatch
        tc.configure_args["--with-ucx"] = "no"  # UCX
        tc.configure_args["--with-valgrind"] = "no"  # Valgrind
        if Version(self.version) >= "5.0":
            tc.configure_args["--with-curl"] = root("libcurl") if self.options.with_curl else "no"
            tc.configure_args["--with-jansson"] = root("jansson") if self.options.with_jansson else "no"
            tc.configure_args["--with-prrte"] = "internal"  # PMIx runtime
            tc.configure_args["--enable-sphinx"] = "no"  # only used for docs
            tc.configure_args["--with-argobots"] = "no"  # argobots
            tc.configure_args["--with-cxi"] = "no"  # CXI
            tc.configure_args["--with-libev"] = "no"  # not compatible with libevent, which cannot be disabled as of v5.0.5
            tc.configure_args["--with-munge"] = "no"  # munge
            tc.configure_args["--with-qthreads"] = "no"  # QThreads
            tc.configure_args["--with-rocm"] = "no"  # ROCm
        else:
            tc.configure_args["--enable-mpi-cxx"] = yes_no(self.options.enable_cxx)
            tc.configure_args["--enable-cxx-exceptions"] = yes_no(self.options.get_safe("enable_cxx_exceptions"))
            tc.configure_args["--with-verbs"] = root("rdma-core") if self.options.get_safe("with_verbs") else "no"
            tc.configure_args["--with-fca"] = "no"  # FCA
            tc.configure_args["--with-mxm"] = "no"  # Mellanox MXM
            tc.configure_args["--with-pmi"] = "no"  # PMI
            tc.configure_args["--with-psm"] = "no"  # PSM
            tc.configure_args["--with-xpmem"] = "no"  # XPMEM
            tc.configure_args["--with-x"] = "no"  # X11
        if is_apple_os(self):
            if self.settings.arch == "armv8":
                tc.configure_args["--host"] = "aarch64-apple-darwin"
                tc.extra_ldflags.append("-arch arm64")
            # macOS has no libnl
            tc.configure_args["--enable-mca-no-build"] = "reachable-netlink"
        # libtool's libltdl is not really needed, OpenMPI provides its own equivalent.
        # Not adding it as it fails to be detected by ./configure in some cases.
        # https://github.com/open-mpi/ompi/blob/v4.1.6/opal/mca/dl/dl.h#L20-L25
        tc.configure_args["--with-libltdl"] = "no"
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

        # Needed for ./configure to find libhwloc.so and libibnetdisc.so
        VirtualRunEnv(self).generate(scope="build")

        # TODO: might want to enable reproducible builds by setting
        #  $SOURCE_DATE_EPOCH, $USER and $HOSTNAME

    def _patch_sources(self):
        # Not needed and fails with v5.0 due to additional Python dependencies
        save(self, os.path.join(self.source_folder, "docs", "Makefile.in"), "all:\ninstall:\n")
        # Workaround for <cstddef> trying to include VERSION from source dir due to a case-insensitive filesystem on macOS
        # Based on https://github.com/macports/macports-ports/blob/22dded99ae76a287f04a9685bbc820ecaa397fea/science/openmpi/files/patch-configure.diff
        if Version(self.version) >= "5.0":
            replace_in_file(self, os.path.join(self.source_folder, "configure"),
                            "-I$(srcdir) ", "-idirafter$(srcdir) ")
        else:
            replace_in_file(self, os.path.join(self.source_folder, "configure"),
                            "-I$(top_srcdir) ", "-idirafter$(top_srcdir) ")

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
        rmdir(self, os.path.join(self.package_folder, "res", "doc"))
        rmdir(self, os.path.join(self.package_folder, "res", "man"))
        rm(self, "*.la", self.package_folder, recursive=True)
        fix_apple_shared_install_name(self)

    def package_info(self):
        # Based on https://cmake.org/cmake/help/latest/module/FindMPI.html#variables-for-using-mpi
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "MPI")
        # TODO: Use None when available as Conan feature.
        self.cpp_info.set_property("pkg_config_name", "_ompi-do-not-use")
        # TODO: export a .cmake module to correctly set all variables set by CMake's FindMPI.cmake

        requires = [
            "hwloc::hwloc",
            "libevent::libevent",
            "zlib::zlib",
        ]
        if self.settings.os == "Linux":
            requires.append("libnl::libnl")
        if self.options.get_safe("with_curl"):
            requires.append("libcurl::libcurl")
        if self.options.get_safe("with_jansson"):
            requires.append("jansson::jansson")
        if self.options.get_safe("with_libfabric"):
            requires.append("libfabric::libfabric")
        if self.options.get_safe("with_verbs"):
            requires.extend(["rdma-core::libibverbs", "rdma-core::librdmacm"])

        # The components are modelled based on OpenMPI's pkg-config files
        self.cpp_info.components["ompi"].set_property("pkg_config_name", "ompi")
        self.cpp_info.components["ompi"].libs = ["mpi"]

        if Version(self.version) >= "5.0":
            self.cpp_info.components["pmix"].set_property("pkg_config_name", "pmix")
            self.cpp_info.components["pmix"].libs = ["pmix"]
            self.cpp_info.components["prrte"].set_property("pkg_config_name", "prrte")
            self.cpp_info.components["prrte"].libs = ["prrte"]
            self.cpp_info.components["prrte"].requires = ["pmix"]
            self.cpp_info.components["ompi"].requires = ["pmix"]
            main_component = self.cpp_info.components["ompi"]
        else:
            self.cpp_info.components["orte"].set_property("pkg_config_name", "orte")
            self.cpp_info.components["orte"].libs = ["open-rte"]
            self.cpp_info.components["ompi"].requires = ["orte"]
            main_component = self.cpp_info.components["orte"]

        main_component.libs.append("open-pal")
        main_component.includedirs.append(os.path.join("include", "openmpi"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            main_component.system_libs = ["m", "dl", "pthread", "rt", "util"]
        main_component.cflags = ["-pthread"]
        main_component.requires += requires

        if Version(self.version) < "5.0":
            self.cpp_info.components["ompitrace"].set_property("pkg_config_name", "ompitrace")
            self.cpp_info.components["ompitrace"].libs = ["ompitrace"]
            self.cpp_info.components["ompitrace"].requires = ["ompi"]

        self.cpp_info.components["ompi-c"].set_property("pkg_config_name", "ompi-c")
        self.cpp_info.components["ompi-c"].set_property("cmake_target_name", "MPI::MPI_C")
        self.cpp_info.components["ompi-c"].requires = ["ompi"]

        if self.options.get_safe("enable_cxx"):
            self.cpp_info.components["ompi-cxx"].set_property("pkg_config_name", "ompi-cxx")
            self.cpp_info.components["ompi-cxx"].set_property("cmake_target_name", "MPI::MPI_CXX")
            self.cpp_info.components["ompi-cxx"].libs = ["mpi_cxx"]
            self.cpp_info.components["ompi-cxx"].requires = ["ompi"]
            if self.options.enable_cxx_exceptions:
                self.cpp_info.components["orte"].cflags.append("-fexceptions")

        if self.options.fortran != "no":
            self.cpp_info.components["ompi-fort"].set_property("pkg_config_name", "ompi-fort")
            self.cpp_info.components["ompi-fort"].set_property("cmake_target_name", "MPI::MPI_Fortran")
            self.cpp_info.components["ompi-fort"].libs = ["mpi_mpifh"]
            self.cpp_info.components["ompi-fort"].requires = ["ompi"]
            # Aliases
            self.cpp_info.components["ompi-f77"].set_property("pkg_config_name", "ompi-f77")
            self.cpp_info.components["ompi-f77"].requires = ["ompi-fort"]
            self.cpp_info.components["ompi-f90"].set_property("pkg_config_name", "ompi-f90")
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
