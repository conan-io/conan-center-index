import os
import shutil

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import get, rm, rmdir, patch, mkdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.56.0 <2 || >=2.0.6"


class PackageConan(ConanFile):
    name = "coin-mumps"
    description = "MUltifrontal Massively Parallel sparse direct Solver (MUMPS)"
    license = "CECILL-C", "BSD 3-Clause", "EPL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/coin-or-tools/ThirdParty-Mumps"
    topics = ("solver", "sparse", "direct", "parallel", "linear-algebra")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "intsize": [32, 64],
        "precision": ["single", "double", "all"],
        "with_lapack": [True, False],
        "with_metis": [True, False],
        "with_openmp": [True, False],
        "with_pthread": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "intsize": 32,
        "precision": "double",
        "with_lapack": True,
        "with_metis": True,
        "with_openmp": False,
        "with_pthread": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openmpi/4.1.6")
        if self.options.with_lapack:
            self.requires("openblas/0.3.25")
        if self.options.with_metis:
            self.requires("metis/5.2.1")
        if self.options.with_openmp and self.settings.compiler in ["clang", "apple-clang"]:
            self.requires("llvm-openmp/17.0.4")
        self.requires("gcc/13.2.0", headers=False, libs=True)

    def validate(self):
        if self.options.with_lapack and not self.dependencies["openblas"].options.build_lapack:
            raise ConanInvalidConfiguration("MUMPS requires openblas with build_lapack=True")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.1.0")
        # Require GCC for gfortran
        self.build_requires("gcc/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["build_scripts"], strip_root=True)
        get(self, **self.conan_data["sources"][self.version]["source"], destination="MUMPS", strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            f"--enable-pthread-mumps={yes_no(self.options.with_pthread)}",
            f"--enable-openmp={yes_no(self.options.with_openmp)}",
            f"--with-lapack={yes_no(self.options.with_lapack)}",
            f"--with-metis={yes_no(self.options.with_metis)}",
            f"--with-precision={self.options.precision}",
            f"--with-intsize={self.options.intsize}",
        ])
        if self.options.with_lapack:
            dep_info = self.dependencies["openblas"].cpp_info.aggregated_components()
            lib_flags = " ".join([f"-l{lib}" for lib in dep_info.libs + dep_info.system_libs])
            tc.configure_args.append(f"--with-lapack-lflags=-L{dep_info.libdir} {lib_flags}")
        tc.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def _patch_sources(self):
        # https://github.com/coin-or-tools/ThirdParty-Mumps/blob/releases/3.0.5/get.Mumps#L63-L67
        patch(self, self.source_folder, os.path.join(self.source_folder, "mumps_mpi.patch"))
        os.rename(os.path.join(self.source_folder, "MUMPS", "libseq", "mpi.h"),
                  os.path.join(self.source_folder, "MUMPS", "libseq", "mumps_mpi.h"))

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        mkdir(self, os.path.join(self.package_folder, "licenses"))
        shutil.copy(os.path.join(self.source_folder, "LICENSE"),
                    os.path.join(self.package_folder, "licenses", "LICENSE-ThirdParty-Mumps"))
        shutil.copy(os.path.join(self.source_folder, "MUMPS", "LICENSE"),
                    os.path.join(self.package_folder, "licenses", "LICENSE-MUMPS"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "coinmumps")
        self.cpp_info.libs = ["coinmumps"]
        self.cpp_info.includedirs.append(os.path.join("include", "coin-or"))
        self.cpp_info.includedirs.append(os.path.join("include", "coin-or", "mumps"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m"])
            if self.options.with_pthread:
                self.cpp_info.system_libs.extend(["pthread"])

        if self.options.with_openmp:
            if is_msvc(self):
                openmp_flags = ["-openmp"]
            elif self.settings.compiler in ("gcc", "clang"):
                openmp_flags = ["-fopenmp"]
            elif self.settings.compiler == "apple-clang":
                openmp_flags = ["-Xpreprocessor", "-fopenmp"]
            else:
                openmp_flags = []
            self.cpp_info.exelinkflags = openmp_flags
            self.cpp_info.sharedlinkflags = openmp_flags

        self.cpp_info.requires = ["openmpi::ompi-c"]
        if self.options.with_lapack:
            self.cpp_info.requires.append("openblas::openblas")
        if self.options.with_metis:
            self.cpp_info.requires.append("metis::metis")
        if self.options.with_openmp and self.settings.compiler in ["clang", "apple-clang"]:
            self.cpp_info.requires.append("llvm-openmp::llvm-openmp")
        self.cpp_info.requires.extend(["gcc::gfortran", "gcc::quadmath"])
