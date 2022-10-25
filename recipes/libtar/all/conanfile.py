from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualRunEnv
from conan.tools.files import copy, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class LibTarConan(ConanFile):
    name = "libtar"
    description = "libtar is a library for manipulating tar files from within C programs."
    topics = ("libtar", "tar")
    license = "BSD-3-Clause"
    homepage = "https://repo.or.cz/libtar.git"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

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
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")

    def validate(self):
        if self.info.settings.os == "Windows":
            raise ConanInvalidConfiguration("libtar does not support Windows")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--with-zlib" if self.options.with_zlib else "--without-zlib",
        ])
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

    def _patch_sources(self):
        if self.options.with_zlib:
            replace_in_file(
                self,
                os.path.join(self.source_folder, "configure.ac"),
                "AC_CHECK_LIB([z], [gzread])",
                "AC_CHECK_LIB([{}], [gzread])".format(self.dependencies["zlib"].cpp_info.libs[0]),
            )

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.autoreconf()
        # TODO: use fix_apple_shared_install_name(self) instead, once https://github.com/conan-io/conan/issues/12107 fixed
        replace_in_file(self, os.path.join(self.source_folder, "configure"), "-install_name \\$rpath/", "-install_name @rpath/")
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYRIGHT", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["tar"]

        # TODO: to remove in conan v2
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.deps_env_info.PATH.append(bin_path)
