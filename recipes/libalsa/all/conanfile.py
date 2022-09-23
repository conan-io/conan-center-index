from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import unix_path
import os

required_conan_version = ">=1.50.0"


class LibalsaConan(ConanFile):
    name = "libalsa"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/alsa-project/alsa-lib"
    topics = ("libalsa", "alsa", "sound", "audio", "midi")
    description = "Library of ALSA: The Advanced Linux Sound Architecture, that provides audio " \
                  "and MIDI functionality to the Linux operating system"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disable_python": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disable_python": True,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Only Linux supported")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            f"--enable-python={yes_no(not self.options.disable_python)}",
            "--datarootdir=${prefix}/res",
            "--datadir=${prefix}/res",
        ])
        tc.generate()
        env = VirtualBuildEnv(self)
        env.generate()

    def build(self):
        apply_conandata_patches(self)
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "ALSA")
        self.cpp_info.set_property("cmake_target_name", "ALSA::ALSA")
        self.cpp_info.set_property("pkg_config_name", "alsa")
        self.cpp_info.libs = ["asound"]
        self.cpp_info.resdirs = ["res"]
        self.cpp_info.system_libs = ["dl", "m", "rt", "pthread"]
        alsa_config_dir = os.path.join(self.package_folder, "res", "alsa")
        self.runenv_info.define_path("ALSA_CONFIG_DIR", alsa_config_dir)

        # TODO: to remove in conan v2?
        self.cpp_info.names["cmake_find_package"] = "ALSA"
        self.cpp_info.names["cmake_find_package_multi"] = "ALSA"
        self.cpp_info.names["pkg_config"] = "alsa"
        self.env_info.ALSA_CONFIG_DIR = alsa_config_dir
