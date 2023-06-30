from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, rename, chdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.env import VirtualBuildEnv
from conan.tools.layout import basic_layout
from conan.tools.build import cross_building
from conan.tools.microsoft import is_msvc, NMakeToolchain
import os


required_conan_version = ">=1.53.0"


class LibTomMathConan(ConanFile):
    name = "libtommath"
    description = "LibTomMath is a free open source portable number theoretic multiple-precision integer library written entirely in C."
    topics = "libtommath", "math", "multiple", "precision"
    license = "Unlicense"
    homepage = "https://www.libtom.net/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
                self.tool_requires("pkgconf/1.9.3")
        if not is_msvc(self) and self.settings.os != "Windows" and self.options.shared:
            self.tool_requires("libtool/2.4.7")

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if is_msvc(self):
            tc = NMakeToolchain(self)
            tc.extra_ldflags = ["-lcrypt32"]
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            if self.settings.os == "Macos" and self.settings.arch == "armv8":
                tc.extra_ldflags.append("-arch arm64")
                if cross_building(self):
                    tc.make_args.append("CROSS_COMPILE=arm64-apple-m1-")
            tc.make_args.extend([f"PREFIX={self.package_folder}", "LIBTOOL=libtool"])
            tc.generate()

    @property
    def _makefile_filename(self):
        if is_msvc(self):
            return "makefile.msvc"
        elif self.settings.os == "Windows" and not is_msvc(self):
            return "makefile.mingw"
        elif self.options.shared:
            return "makefile.shared"
        else:
            return "makefile.unix"

    @property
    def _makefile_target(self):
        if is_msvc(self):
            return "tommath.dll" if self.options.shared else "tommath.lib"
        elif self.settings.os == "Windows" and not is_msvc(self):
            return "libtommath.dll" if self.options.shared else "libtommath.a"
        return None

    def build(self):
        apply_conandata_patches(self)
        with chdir(self, self.source_folder):
            if is_msvc(self):
                self.run(f"nmake -f {self._makefile_filename} {self._makefile_target}")
            else:
                autotools = Autotools(self)
                autotools.make(target=self._makefile_target, args=["-f", self._makefile_filename])

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if self.settings.os == "Windows":
            # INFO: The mingw makefile uses `cmd`, which is only available on Windows
            copy(self, "*.a", src=self.source_folder, dst=os.path.join(self.package_folder, "lib"))
            copy(self, "*.lib", src=self.source_folder, dst=os.path.join(self.package_folder, "lib"))
            copy(self, "*.dll", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"))
            copy(self, "tommath.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
        else:
            with chdir(self, self.source_folder):
                if is_msvc(self):
                    self.run(f"nmake -f {self._makefile_filename} install")
                else:
                    autotools = Autotools(self)
                    autotools.install(args=["DESTDIR=", "-f", self._makefile_filename])

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        if self.options.shared:
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        if is_msvc(self) and self.options.shared:
            rename(self, os.path.join(self.package_folder, "lib", "tommath.dll.lib"),
                   os.path.join(self.package_folder, "lib", "tommath.lib"))

    def package_info(self):
        self.cpp_info.libs = ["tommath"]
        if not self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.system_libs = ["advapi32", "crypt32"]

        self.cpp_info.set_property("cmake_file_name", "libtommath")
        self.cpp_info.set_property("cmake_target_name", "libtommath")
        self.cpp_info.set_property("pkg_config_name", "libtommath")
