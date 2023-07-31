import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path

required_conan_version = ">=1.53.0"


class LibRHashConan(ConanFile):
    name = "librhash"
    description = "Great utility for computing hash sums"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://rhash.sourceforge.net/"
    topics = ("rhash", "hash", "checksum")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

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
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("Visual Studio is not supported")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        if self.settings.compiler in ("apple-clang",):
            if self.settings.arch == "armv7":
                tc.build_type_link_flags.append("-arch armv7")
            elif self.settings.arch == "armv8":
                tc.build_type_link_flags.append("-arch arm64")
        tc.configure_args = [
            # librhash's configure script does not understand `--enable-opt1=yes`
            "--{}-openssl".format("enable" if self.options.with_openssl else "disable"),
            "--disable-gettext",
            # librhash's configure script is custom and does not understand "--bindir=${prefix}/bin" arguments
            f"--prefix={unix_path(self, self.package_folder)}",
            f"--bindir=/bin",
            f"--libdir=/lib",
        ]
        if self.options.shared:
            tc.configure_args += ["--enable-lib-shared", "--disable-lib-static"]
        else:
            tc.configure_args += ["--disable-lib-shared", "--enable-lib-static"]
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()
            autotools.make(target="install-lib-headers")
            with chdir(self, "librhash"):
                if self.options.shared:
                    autotools.make(target="install-so-link")
        for path in self.package_path.iterdir():
            if path.is_dir() and path.name not in ["include", "lib", "licenses"]:
                rmdir(self, path)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "LibRHash")
        self.cpp_info.set_property("cmake_target_name", "LibRHash::LibRHash")
        self.cpp_info.set_property("pkg_config_name", "librhash")
        self.cpp_info.libs = ["rhash"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "LibRHash"
        self.cpp_info.names["cmake_find_package_multi"] = "LibRHash"
