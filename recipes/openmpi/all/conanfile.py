from conan import ConanFile
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.files import copy, get, rm, rmdir, apply_conandata_patches, export_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.52.0"


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
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # FIXME : self.requires("libevent/2.1.12") - try to use libevent from conan
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
        tc.configure_args.append("--enable-shared={}".format(yes_no(self.options.shared)))
        tc.configure_args.append("--enable-static={}".format(yes_no(not self.options.shared)))
        tc.configure_args.append("--with-pic={}".format(yes_no(self.options.get_safe("fPIC", True))))
        tc.configure_args.append("--enable-mpi-fortran={}".format(str(self.options.fortran)))
        tc.configure_args.append("--with-zlib={}".format(self.deps_cpp_info["zlib"].rootpath))
        tc.configure_args.append("--with-zlib-libdir={}".format(self.deps_cpp_info["zlib"].lib_paths[0]))
        tc.configure_args.append("--datarootdir=${prefix}/res")
        if self.settings.build_type == "Debug":
            tc.configure_args.append("--enable-debug")
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
        remove_files_by_mask(self, os.path.join(self.package_folder, "lib"), "*.la")

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
