import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import XCRun, is_apple_os
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, replace_in_file, rmdir, rm, chdir, download, patch
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.55.0"


class GFortranConan(ConanFile):
    name = "gfortran"
    description = "The Fortran compiler front end and run-time libraries for GCC"
    license = "GPL-3.0-only WITH GCC-exception-3.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gcc.gnu.org/fortran"
    topics = ("fortran", "gcc", "gnu", "compiler")

    # "library" because it also provides libgfortran, libquadmath, etc. in the host context.
    # You will usually need to use the package as both a tool_requires() and a requires() in your recipe.
    # "shared" to keep things simple and to not accidentally mix static and shared libraries during linking.
    package_type = "shared-library"
    settings = "os", "compiler", "arch", "build_type"

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def package_id(self):
        del self.info.settings.compiler

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("mpc/1.3.1")
        self.requires("mpfr/4.2.0")
        self.requires("gmp/6.3.0")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("isl/0.26")

    def validate_build(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("GCC can't be built with MSVC")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(
                "Windows builds aren't currently supported. Contributions to support this are welcome."
            )

    def build_requirements(self):
        if self.settings.os == "Linux":
            # binutils recipe is broken for Macos, and Windows uses tools
            # distributed with msys/mingw
            self.tool_requires("binutils/2.42")
        self.tool_requires("flex/2.6.4")

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["sources"], strip_root=True)
        download(self, **self.conan_data["sources"][self.version]["homebrew-patches"], filename="homebrew.patch")

    def generate(self):
        # Ensure binutils and flex are on the path.
        buildenv = VirtualBuildEnv(self)
        buildenv.generate()

        runenv = VirtualRunEnv(self)
        runenv.generate(scope="build")

        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--enable-languages=fortran")
        tc.configure_args.append("--disable-nls")
        tc.configure_args.append("--disable-multilib")
        tc.configure_args.append("--disable-bootstrap")
        tc.configure_args.append("--disable-fixincludes")
        tc.configure_args.append(f"--with-zlib={self.dependencies['zlib'].package_folder}")
        tc.configure_args.append(f"--with-isl={self.dependencies['isl'].package_folder}")
        tc.configure_args.append(f"--with-gmp={self.dependencies['gmp'].package_folder}")
        tc.configure_args.append(f"--with-mpc={self.dependencies['mpc'].package_folder}")
        tc.configure_args.append(f"--with-mpfr={self.dependencies['mpfr'].package_folder}")
        tc.configure_args.append(f"--with-pkgversion=ConanCenter gfortran {self.version}")
        tc.configure_args.append(f"--program-suffix=-{self.version}")
        tc.configure_args.append(f"--with-bugurl={self.url}/issues")

        if self.settings.os == "Macos":
            xcrun = XCRun(self)
            tc.configure_args.append(f"--with-sysroot={xcrun.sdk_path}")
            # Set native system header dir to ${{sysroot}}/usr/include to
            # isolate installation from the system as much as possible
            tc.configure_args.append("--with-native-system-header-dir=/usr/include")
            tc.make_args.append("BOOT_LDFLAGS=-Wl,-headerpad_max_install_names")
        tc.generate()

        # Don't use AutotoolsDeps here - deps are passed directly in configure_args.
        # Using AutotoolsDeps causes the compiler tests to fail by erroneously adding
        # additional $LIBS to the test compilation

    def build(self):
        if is_apple_os(self):
            patch(self, patch_file=os.path.join(self.source_folder, "homebrew.patch"), base_path=self.source_folder)

        # If building on x86_64, change the default directory name for 64-bit libraries to "lib":
        replace_in_file(self, os.path.join(self.source_folder, "gcc", "config", "i386", "t-linux64"),
                        "m64=../lib64", "m64=../lib", strict=False)

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    @property
    def _gfortran_full_executable(self):
        # e.g. x86_64-pc-linux-gnu
        triplet = os.listdir(os.path.join(self.package_folder, "lib", "gcc"))[0]
        return f"{triplet}-gfortran-{self.version}"

    def package(self):
        copy(self, "COPYING*", self.source_folder, os.path.join(self.package_folder, "licenses"), keep_path=False)
        autotools = Autotools(self)
        autotools.install(target="install-strip")
        rm(self, "*.la", self.package_folder, recursive=True)
        rmdir(self, os.path.join(self.package_folder, "share"))

        # Don't export static libraries.
        # This only removes libssp_nonshared.a as of v13.2.
        rm(self, "*.a", os.path.join(self.package_folder, "lib"))

        # Drop ar, nm, ranlib, cpp, etc. to not clash with the existing C/C++ toolchain
        for f in self.package_path.joinpath("bin").iterdir():
            if f.name != self._gfortran_full_executable:
                f.unlink()
        with chdir(self, os.path.join(self.package_folder, "bin")):
            os.symlink(self._gfortran_full_executable, f"gfortran-{self.version}")
            os.symlink(self._gfortran_full_executable, "gfortran")

    def package_info(self):
        # Make sure to always include
        # self.requires.expand(["gfortran::libgfortran"])
        # in consuming packages to not overlink to all the components listed below.

        # libgfortran.so: GNU Fortran Library
        self.cpp_info.components["libgfortran"].libs = ["gfortran"]
        self.cpp_info.components["libgfortran"].requires = ["libgcc_s"]
        # libquadmath.so: GCC Quad Precision Math Library
        self.cpp_info.components["libquadmath"].libs = ["quadmath"]
        # libgomp.so: GNU Offloading and Multi-Processing Project
        self.cpp_info.components["libgomp"].libs = ["gomp"]
        # libatomic.so: GNU atomic library
        self.cpp_info.components["libatomic"].libs = ["atomic"]
        # libgcc_s.so: Dynamic gcc runtime
        self.cpp_info.components["libgcc_s"].libs = ["gcc_s"]
        # libssp.so: Stack Smashing Protector library
        self.cpp_info.components["libssp"].libs = ["ssp"]

        self.cpp_info.components["executables"].bindirs = ["bin", "libexec"]
        self.cpp_info.components["executables"].requires = [
            "mpc::mpc",
            "mpfr::mpfr",
            "gmp::gmp",
            "zlib::zlib",
            "isl::isl",
        ]

        gfortran_path = os.path.join(self.package_folder, "bin", self._gfortran_full_executable)
        self.buildenv_info.define_path("FC", gfortran_path)

        # TODO: Legacy, remove when Conan v1 support is dropped
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.FC = gfortran_path
