import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMakeToolchain, CMake
from conan.tools.files import get, copy, download, export_conandata_patches, apply_conandata_patches, chdir, mkdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, NMakeToolchain, VCVars

required_conan_version = ">=1.54.0"


class F2cConan(ConanFile):
    name = "f2c"
    description = "Fortran 77 to C/C++ translator"
    license = "SMLNJ"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://netlib.org/f2c/"
    topics = ("fortran", "translator")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cxx_support": [True, False],
        "fc_wrapper": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "cxx_support": True,
        "fc_wrapper": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, os.path.join(self.export_sources_folder, "src", "f2c"))
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.options.fc_wrapper

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("shared builds are not supported on Windows")

    @staticmethod
    def _chmod_plus_x(name):
        if os.name == "posix":
            os.chmod(name, os.stat(name).st_mode | 0o111)

    def source(self):
        mkdir(self, "f2c")
        mkdir(self, "libf2c")
        with chdir(self, "f2c"):
            get(self, **self.conan_data["sources"][self.version]["f2c"], strip_root=True)
            download(self, **self.conan_data["sources"][self.version]["fc"], filename="fc")
            self._chmod_plus_x("fc")
        with chdir(self, "libf2c"):
            get(self, **self.conan_data["sources"][self.version]["libf2c"])

    def generate(self):
        # f2c
        tc = CMakeToolchain(self)
        tc.generate()

        # libf2c
        if is_msvc(self):
            VCVars(self).generate()
            tc = NMakeToolchain(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            defines = list(tc.defines)
            if self.settings.os == "Linux":
                defines.append("NON_UNIX_STDIO")
            elif not is_apple_os(self) and self.settings.os != "Windows":
                defines.append("USE_STRLEN")
            cflags = list(tc.cflags)
            if self.options.get_safe("fPIC", True):
                cflags.append("-fPIC")
            cflags += [f"-D{d}" for d in defines]
            tc.make_args += [
                f"CFLAGS={' '.join(cflags)}",
                f"LDFLAGS={' '.join(tc.ldflags)}"
            ]
            tc.generate()

    @property
    def _target(self):
        if is_msvc(self):
            return None
        if not self.options.shared:
            return "static"
        if is_apple_os(self):
            return "shared_dylib"
        return "shared_so"

    def _build_libf2c(self):
        with chdir(self, os.path.join(self.source_folder, "libf2c")):
            if is_msvc(self):
                # FIXME: hadd is not available in makefile.vc
                # if self.options.cxx_support:
                #     self.run("nmake /f makefile.vc hadd")
                self.run("nmake /f makefile.vc")
            else:
                autotools = Autotools(self)
                if self.options.cxx_support:
                    autotools.make(args=["-f", "makefile.u"], target="hadd")
                autotools.make(args=["-f", "makefile.u"], target=self._target)

    def _build_f2c(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "f2c"))
        cmake.build()

    def build(self):
        apply_conandata_patches(self)
        self._build_libf2c()
        self._build_f2c()

    def package(self):
        copy(self, "Notice", os.path.join(self.source_folder, "f2c"), os.path.join(self.package_folder, "licenses"))

        #f2c
        cmake = CMake(self)
        cmake.install()
        copy(self, "fc", os.path.join(self.source_folder, "f2c"), os.path.join(self.package_folder, "bin"))

        # libf2c
        libf2c_dir = os.path.join(self.source_folder, "libf2c")
        if is_msvc(self):
            copy(self, "vcf2c.lib", libf2c_dir, os.path.join(self.package_folder, "lib"))
        elif not self.options.shared:
            copy(self, "libf2c.a", libf2c_dir, os.path.join(self.package_folder, "lib"))
        elif is_apple_os(self):
            copy(self, "libf2c.dylib", libf2c_dir, os.path.join(self.package_folder, "lib"))
        else:
            copy(self, "libf2c.so.2.1", libf2c_dir, os.path.join(self.package_folder, "lib"))
            self.run("ln -s libf2c.so.2.1 libf2c.so.2", cwd=os.path.join(self.package_folder, "lib"))
            self.run("ln -s libf2c.so.2.1 libf2c.so", cwd=os.path.join(self.package_folder, "lib"))
        copy(self, "f2c.h", libf2c_dir, os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.libs = ["vcf2c" if is_msvc(self) else "f2c"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]

        f2c_path = os.path.join(self.package_folder, "bin", "f2c")
        self.buildenv_info.define_path("F2C", f2c_path)

        if self.options.fc_wrapper:
            fc_path = os.path.join(self.package_folder, "bin", "fc")
            includedir = os.path.join(self.package_folder, "include")
            libdir = os.path.join(self.package_folder, "lib")
            if is_msvc(self):
                cflags = f"-I{includedir} -link /LIBPATH:{libdir} vcf2c.lib"
            else:
                cflags = f"-I{includedir} -L{libdir} -lf2c"
            self.buildenv_info.define_path("FC", fc_path)
            self.buildenv_info.define("CFLAGSF2C", cflags)
            self.env_info.FC = fc_path
            self.env_info.CFLAGSF2C = cflags

        # TODO: Legacy, to be removed on Conan 2.0
        bin_folder = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_folder)
        self.env_info.F2C = f2c_path
