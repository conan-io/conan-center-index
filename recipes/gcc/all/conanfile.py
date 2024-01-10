from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.errors import ConanInvalidConfiguration
from conan.tools.layout import basic_layout
from conan.tools.apple import XCRun
from conan.tools.files import copy, get, replace_in_file, rmdir, rm
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.55.0"


class GccConan(ConanFile):
    name = "gcc"
    description = (
        "The GNU Compiler Collection includes front ends for C, "
        "C++, Objective-C, Fortran, Ada, Go, and D, as well as "
        "libraries for these languages (libstdc++,...). "
    )
    license = "GPL-3.0-only WITH GCC-exception-3.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gcc.gnu.org"
    topics = ("gcc", "gnu", "compiler", "c", "c++")

    package_type = "library"
    settings = "os", "compiler", "arch", "build_type"

    def configure(self):
        if self.settings.compiler in ["clang", "apple-clang"]:
            # Can't remove this from cxxflags with autotools - so get rid of it
            self.settings.rm_safe("compiler.libcxx")
        # Do not override the C++11 cppstd set by the project
        # Otherwise fails to compile with C++17 (for GCC v12)
        self.settings.rm_safe("compiler.cppstd")

    def build_requirements(self):
        if self.settings.os == "Linux":
            # binutils recipe is broken for Macos, and Windows uses tools
            # distributed with msys/mingw
            self.tool_requires("binutils/2.41")
        self.tool_requires("flex/2.6.4")

    def requirements(self):
        self.requires("mpc/1.3.1")
        self.requires("mpfr/4.2.0")
        self.requires("gmp/6.3.0")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("isl/0.25")

    def package_id(self):
        del self.info.settings.compiler

    def validate_build(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("GCC can't be built with MSVC")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(
                "Windows builds aren't currently supported. Contributions to support this are welcome."
            )
        if self.settings.os == "Macos":
            # FIXME: This recipe should largely support Macos, however the following
            # errors are present when building using the c3i CI:
            # clang: error: unsupported option '-print-multi-os-directory'
            # clang: error: no input files
            raise ConanInvalidConfiguration(
                "Macos builds aren't currently supported. Contributions to support this are welcome."
            )
        if cross_building(self):
            raise ConanInvalidConfiguration(
                "Cross builds are not current supported. Contributions to support this are welcome"
            )

    def layout(self):
        basic_layout(self, src_folder="src")

    def generate(self):
        # Ensure binutils and flex are on the path.
        buildenv = VirtualBuildEnv(self)
        buildenv.generate()

        runenv = VirtualRunEnv(self)
        runenv.generate(scope="build")

        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--enable-languages=c,c++,fortran")
        tc.configure_args.append("--disable-nls")
        tc.configure_args.append("--disable-multilib")
        tc.configure_args.append("--disable-bootstrap")
        tc.configure_args.append(f"--with-zlib={self.dependencies['zlib'].package_folder}")
        tc.configure_args.append(f"--with-isl={self.dependencies['isl'].package_folder}")
        tc.configure_args.append(f"--with-gmp={self.dependencies['gmp'].package_folder}")
        tc.configure_args.append(f"--with-mpc={self.dependencies['mpc'].package_folder}")
        tc.configure_args.append(f"--with-mpfr={self.dependencies['mpfr'].package_folder}")
        tc.configure_args.append(f"--with-pkgversion=conan GCC {self.version}")
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

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        # If building on x86_64, change the default directory name for 64-bit libraries to "lib":
        replace_in_file(
            self,
            os.path.join(self.source_folder, "gcc", "config", "i386", "t-linux64"),
            "m64=../lib64",
            "m64=../lib",
            strict=False,
        )

        # Ensure correct install names when linking against libgcc_s;
        # see discussion in https://github.com/Homebrew/legacy-homebrew/pull/34303
        replace_in_file(
            self,
            os.path.join(self.source_folder, "libgcc", "config", "t-slibgcc-darwin"),
            "@shlib_slibdir@",
            os.path.join(self.package_folder, "lib"),
            strict=False,
        )

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install(target="install-strip")

        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", self.package_folder, recursive=True)
        copy(self, "COPYING*",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder,
             keep_path=False)

    def package_info(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "rt", "pthread", "dl"]

        def define_tool_var(var, name):
            path = os.path.join(self.package_folder, "bin", f"{name}-{self.version}")
            self.buildenv_info.define_path(var, path)
            # TODO: Remove after conan 2.0 is released
            setattr(self.env_info, var, path)

        define_tool_var("CC", "gcc")
        define_tool_var("CXX", "g++")
        define_tool_var("FC", "gfortran")
        define_tool_var("AR", "gcc-ar")
        define_tool_var("NM", "gcc-nm")
        define_tool_var("RANLIB", "gcc-ranlib")

        # Libs
        # Shared            | Static
        # ==================|====================
        # libitm.so         | libitm.a              # GNU Transactional Memory Library. Transaction support for accesses to a process' memory, enabling easy-to-use synchronization of accesses to shared memory by several threads
        # libgfortran.so    | libgfortran.a         # GNU Fortran Library
        # libgomp.so        | libgomp.a             # GNU Offloading and Multi-Processing Project
        # libubsan.so       | libubsan.a            # Undefined Behaviour sanitizer
        # libtsan.so        | libtsan.a             # Thread sanitizer
        # libstdc++.so      | libstdc++.a           # C++ Standard library
        # libgcc_s.so       |                       # Dynamic gcc runtime. Combination of libgcc and libgcc_eh? Used by -shared-libgcc
        # libcc1.so         |                       # GCC cc1 plugin for gdb
        # liblsan.so        | liblsan.a             # Leak sanitizer
        # libasan.so        | libasan.so            # Address sanitizer
        # libssp.so         | libssp.a              # Stack Smashing Protector library
        # libquadmath.so    | libquadmath.a         # GCC Quad Precision Math Library
        # libcp1plugin.so   |                       # Library interface to C++ frontend
        # libcc1plugin.so   |                       # Library interface to C frontend
        # libatomic.so      | libatomic.a           # GNU atomic library
        # liblto_plugin.so  |                       # Link time optimization plugin
        #                   | libsupc++.a           # A subset of libstdc++.a. Contains only support routines defined by clause 18 of the standard.
        #                   | libstdc++fs.a         # Experimental extension for std::filesystem
        #                   | libssp_nonshared.a    #
        #                   | libgcc.a              # Static gcc runtime. Used by -static-libgcc
        #                   | libcaf_single.a
        #                   | libgcc_eh.a           # libgcc exception handling. User by -static-libgcc
        #                   | libgcov.a             # test coverage library

        # e.g. x86_64-pc-linux-gnu
        triplet = os.listdir(os.path.join(self.package_folder, "libexec", "gcc"))[0]

        self.cpp_info.set_property("cmake_target_name", "gcc::gcc_all")
        self.cpp_info.bindirs = ["bin", os.path.join("bin", "libexec", "gcc", triplet, self.version)]

        self.cpp_info.components["gcc_eh"].set_property("cmake_target_name", "gcc::gcc_eh")
        self.cpp_info.components["gcc_eh"].libdirs = [os.path.join("lib", "gcc", triplet, self.version)]
        self.cpp_info.components["gcc_eh"].libs = ["gcc_eh"]

        self.cpp_info.components["gcc"].set_property("cmake_target_name", "gcc::gcc")
        self.cpp_info.components["gcc"].libdirs = [os.path.join("lib", "gcc", triplet, self.version)]
        self.cpp_info.components["gcc"].libs = ["gcc"]
        self.cpp_info.components["gcc"].requires = ["gcc_eh"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["gcc"].system_libs.append("m")
            self.cpp_info.components["gcc"].system_libs.append("rt")
            self.cpp_info.components["gcc"].system_libs.append("pthread")
            self.cpp_info.components["gcc"].system_libs.append("dl")

        self.cpp_info.components["gcc_s"].set_property("cmake_target_name", "gcc::gcc_s")
        self.cpp_info.components["gcc_s"].libdirs = ["lib"]
        self.cpp_info.components["gcc_s"].libs = ["gcc_s"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["gcc_s"].system_libs.append("m")
            self.cpp_info.components["gcc_s"].system_libs.append("rt")
            self.cpp_info.components["gcc_s"].system_libs.append("pthread")
            self.cpp_info.components["gcc_s"].system_libs.append("dl")

        self.cpp_info.components["gfortran"].set_property("cmake_target_name", "gcc::gfortran")
        self.cpp_info.components["gfortran"].libdirs = ["lib"]
        self.cpp_info.components["gfortran"].libs = ["gfortran"]
        self.cpp_info.components["gfortran"].requires = ["gcc_s", "quadmath"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["gfortran"].system_libs.append("m")

        self.cpp_info.components["quadmath"].set_property("cmake_target_name", "gcc::quadmath")
        self.cpp_info.components["quadmath"].libdirs = ["lib"]
        self.cpp_info.components["quadmath"].libs = ["quadmath"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["quadmath"].system_libs.append("m")

        self.cpp_info.components["itm"].set_property("cmake_target_name", "gcc::itm")
        self.cpp_info.components["itm"].libdirs = ["lib"]
        self.cpp_info.components["itm"].libs = ["itm"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["itm"].system_libs.append("pthread")

        self.cpp_info.components["tsan"].set_property("cmake_target_name", "gcc::tsan")
        self.cpp_info.components["tsan"].libdirs = ["lib"]
        self.cpp_info.components["tsan"].libs = ["tsan"]
        self.cpp_info.components["tsan"].requires = ["gcc_s", "stdc++"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["tsan"].system_libs.append("pthread")
            self.cpp_info.components["tsan"].system_libs.append("m")
            self.cpp_info.components["tsan"].system_libs.append("dl")

        self.cpp_info.components["stdc++"].set_property("cmake_target_name", "gcc::stdc++")
        self.cpp_info.components["stdc++"].libdirs = ["lib"]
        self.cpp_info.components["stdc++"].libs = ["stdc++"]
        self.cpp_info.components["stdc++"].requires = ["gcc_s"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["stdc++"].system_libs.append("m")

        self.cpp_info.components["stdc++fs"].set_property("cmake_target_name", "gcc::stdc++fs")
        self.cpp_info.components["stdc++fs"].libdirs = ["lib"]
        self.cpp_info.components["stdc++fs"].libs = ["stdc++fs"]

        self.cpp_info.components["supc++"].set_property("cmake_target_name", "gcc::supc++")
        self.cpp_info.components["supc++"].libdirs = ["lib"]
        self.cpp_info.components["supc++"].libs = ["supc++"]

        self.cpp_info.components["ssp"].set_property("cmake_target_name", "gcc::ssp")
        self.cpp_info.components["ssp"].libdirs = ["lib"]
        self.cpp_info.components["ssp"].libs = ["ssp"]

        self.cpp_info.components["ssp_nonshared"].set_property("cmake_target_name", "gcc::ssp_nonshared")
        self.cpp_info.components["ssp_nonshared"].libdirs = ["lib"]
        self.cpp_info.components["ssp_nonshared"].libs = ["ssp_nonshared"]

        self.cpp_info.components["atomic"].set_property("cmake_target_name", "gcc::atomic")
        self.cpp_info.components["atomic"].libdirs = ["lib"]
        self.cpp_info.components["atomic"].libs = ["atomic"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["atomic"].system_libs.append("pthread")

        self.cpp_info.components["gomp"].set_property("cmake_target_name", "gcc::gomp")
        self.cpp_info.components["gomp"].libdirs = ["lib"]
        self.cpp_info.components["gomp"].libs = ["gomp"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["gomp"].system_libs.append("pthread")
            self.cpp_info.components["gomp"].system_libs.append("dl")

        self.cpp_info.components["asan"].set_property("cmake_target_name", "gcc::asan")
        self.cpp_info.components["asan"].libdirs = ["lib"]
        self.cpp_info.components["asan"].libs = ["asan"]
        self.cpp_info.components["asan"].requires = ["gcc_s", "stdc++"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["asan"].system_libs.append("pthread")
            self.cpp_info.components["asan"].system_libs.append("m")
            self.cpp_info.components["asan"].system_libs.append("dl")

        self.cpp_info.components["ubsan"].set_property("cmake_target_name", "gcc::ubsan")
        self.cpp_info.components["ubsan"].libdirs = ["lib"]
        self.cpp_info.components["ubsan"].libs = ["ubsan"]
        self.cpp_info.components["ubsan"].requires = ["gcc_s", "stdc++"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["ubsan"].system_libs.append("pthread")
            self.cpp_info.components["ubsan"].system_libs.append("dl")
            self.cpp_info.components["ubsan"].system_libs.append("rt")

        self.cpp_info.components["lsan"].set_property("cmake_target_name", "gcc::lsan")
        self.cpp_info.components["lsan"].libdirs = ["lib"]
        self.cpp_info.components["lsan"].libs = ["lsan"]
        self.cpp_info.components["lsan"].requires = ["gcc_s", "stdc++"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["lsan"].system_libs.append("pthread")
            self.cpp_info.components["lsan"].system_libs.append("dl")
            self.cpp_info.components["lsan"].system_libs.append("rt")

        self.cpp_info.components["cc1"].set_property("cmake_target_name", "gcc::cc1")
        self.cpp_info.components["cc1"].libdirs = ["lib", "lib64"]
        self.cpp_info.components["cc1"].libs = ["cc1"]
        self.cpp_info.components["cc1"].requires = ["gcc_s", "stdc++"]

        self.cpp_info.components["cp1plugin"].set_property("cmake_target_name", "gcc::cp1plugin")
        self.cpp_info.components["cp1plugin"].libdirs = [os.path.join("lib", "gcc", triplet, self.version, "plugin")]
        self.cpp_info.components["cp1plugin"].libs = ["cp1plugin"]
        self.cpp_info.components["cp1plugin"].requires = ["gcc_s", "stdc++"]

        self.cpp_info.components["cc1plugin"].set_property("cmake_target_name", "gcc::cc1plugin")
        self.cpp_info.components["cc1plugin"].libdirs = [os.path.join("lib", "gcc", triplet, self.version, "plugin")]
        self.cpp_info.components["cc1plugin"].libs = ["cc1plugin"]
        self.cpp_info.components["cc1plugin"].requires = ["gcc_s", "stdc++"]

        self.cpp_info.components["lto_plugin"].set_property("cmake_target_name", "gcc::lto_plugin")
        self.cpp_info.components["lto_plugin"].libdirs = [os.path.join("libexec", "gcc", triplet, self.version)]
        self.cpp_info.components["lto_plugin"].libs = ["lto_plugin"]

        self.cpp_info.components["gcov"].set_property("cmake_target_name", "gcc::gcov")
        self.cpp_info.components["gcov"].libdirs = [os.path.join("lib", "gcc", triplet, self.version)]
        self.cpp_info.components["gcov"].libs = ["gcov"]

        self.cpp_info.components["caf_single"].set_property("cmake_target_name", "gcc::caf_single")
        self.cpp_info.components["caf_single"].libdirs = [os.path.join("lib", "gcc", triplet, self.version)]
        self.cpp_info.components["caf_single"].libs = ["caf_single"]
