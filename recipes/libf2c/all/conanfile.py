import os

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.files import get, copy, export_conandata_patches, apply_conandata_patches, chdir
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.54.0"

class Libf2cConan(ConanFile):
    name = "libf2c"
    description = "Support library for the f2c Fortran 77 to C/C++ translator"
    license = "SMLNJ"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://netlib.org/f2c/"
    topics = ("fortran", "translator", "f2c")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_cxx": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_cxx": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version])

    def generate(self):
        tc = AutotoolsToolchain(self)
        defines = list(tc.defines)
        if self.settings.os == "Linux":
            defines.append("NON_UNIX_STDIO")
        elif self.settings.os in ["FreeBSD", "NetBSD", "OpenBSD", "SunOS"]:
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
    def _makefile(self):
        if is_msvc(self):
            return "makefile.vc"
        return "makefile.u"

    @property
    def _target(self):
        if is_msvc(self):
            return None
        if not self.options.shared:
            return "static"
        if is_apple_os(self):
            return "shared_dylib"
        return "shared_so"

    def build(self):
        apply_conandata_patches(self)
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            if self.options.enable_cxx:
                autotools.make(args=["-f", self._makefile], target="hadd")
            autotools.make(args=["-f", self._makefile], target=self._target)

    def package(self):
        copy(self, "Notice", self.source_folder, os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            pass
        elif not self.options.shared:
            copy(self, "libf2c.a", self.source_folder, os.path.join(self.package_folder, "lib"))
        elif is_apple_os(self):
            copy(self, "libf2c.dylib", self.source_folder, os.path.join(self.package_folder, "lib"))
        else:
            copy(self, "libf2c.so.2.1", self.source_folder, os.path.join(self.package_folder, "lib"))
            self.run("ln -s libf2c.so.2.1 libf2c.so.2", cwd=os.path.join(self.package_folder, "lib"))
            self.run("ln -s libf2c.so.2.1 libf2c.so", cwd=os.path.join(self.package_folder, "lib"))
        copy(self, "f2c.h", self.source_folder, os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.libs = ["f2c"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]

