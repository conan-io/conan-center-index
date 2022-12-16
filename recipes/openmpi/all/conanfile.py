from conan import ConanFile
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.build import cross_building
from conan.tools.files import copy, get, rmdir, rm
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class OpenMPIConan(ConanFile):
    name = "openmpi"
    homepage = "https://www.open-mpi.org"
    url = "https://github.com/conan-io/conan-center-index"
    topics = "mpi", "openmpi"
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


    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
            self.settings.rm_safe("compiler.libcxx")
            self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # TODO FIX :
        #  OpenMPI will compile with this, but,
        #  hdf5 (as a consumer) wont compile with this enabled,
        #   find_package(MPI) fails, probably because the configure test
        #   tries to link to the mpi libs, but probably doesn't also
        #   link in the required libevent libraries ...
        #   I was not able to confirm this theory.
        # self.requires("libevent/2.1.12")
        # -------------------------------------
        self.requires("zlib/1.2.13")
        # used for hwloc component...
        self.requires("libudev/system")
        self.requires("libpciaccess/0.16")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("OpenMPI doesn't support Windows")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.append("--disable-wrapper-rpath")
        tc.configure_args.append("--disable-wrapper-runpath")
        tc.configure_args.append(f"--enable-shared={yes_no(self.options.shared)}")
        tc.configure_args.append(f"--enable-static={yes_no(not self.options.shared)}")
        tc.configure_args.append(f"--with-pic={yes_no(self.options.get_safe('fPIC', True))}")
        tc.configure_args.append(f"--enable-mpi-fortran={str(self.options.fortran)}")
        tc.configure_args.append(f"--with-zlib={self.deps_cpp_info['zlib'].rootpath}")
        tc.configure_args.append(f"--with-zlib-libdir={self.deps_cpp_info['zlib'].lib_paths[0]}")
        tc.configure_args.append("--datarootdir=${prefix}/res")
        if self.settings.build_type == "Debug":
            tc.configure_args.append("--enable-debug")
        tc.configure_args.append(f"PACKAGE_VERSION={Version(self.version)}")
        tc.generate()

        tc = AutotoolsDeps(self)
        tc.generate()

        env = VirtualBuildEnv(self)
        env.generate()

        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "etc"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["mpi", "open-rte", "open-pal"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "dl", "pthread", "rt", "util"])

        self.output.info("Creating MPI_HOME environment variable: {self.package_folder}")
        self.env_info.MPI_HOME = self.package_folder
        self.output.info("Creating OPAL_PREFIX environment variable: {self.package_folder}")
        self.env_info.OPAL_PREFIX = self.package_folder
        mpi_bin = os.path.join(self.package_folder, "bin")
        self.output.info("Creating MPI_BIN environment variable: {mpi_bin}")
        self.env_info.MPI_BIN = mpi_bin
        self.output.info("Appending PATH environment variable: {mpi_bin}")
        self.env_info.PATH.append(mpi_bin)
