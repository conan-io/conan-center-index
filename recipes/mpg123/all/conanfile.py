from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.cmake import cmake_layout, CMake, CMakeDeps, CMakeToolchain
from conan.tools.layout import basic_layout
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.files import get, copy, export_conandata_patches, apply_conandata_patches, rmdir, rm
from conan.tools.microsoft import is_msvc
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.build import cross_building
import os

required_conan_version = ">=1.53.0"


class Mpg123Conan(ConanFile):
    name = "mpg123"
    description = "Fast console MPEG Audio Player and decoder library"
    topics = ("mpeg", "audio", "player", "decoder")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://mpg123.org/"
    license = "LGPL-2.1-or-later", "GPL-2.0-or-later"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "flexible_resampling": [True, False],
        "network": [True, False],
        "icy": [True, False],
        "id3v2": [True, False],
        "ieeefloat": [True, False],
        "layer1": [True, False],
        "layer2": [True, False],
        "layer3": [True, False],
        "moreinfo": [True, False],
        "seektable": [None, "ANY"],
        "module": ["dummy", "libalsa", "tinyalsa", "win32"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "flexible_resampling": True,
        "network": True,
        "icy": True,
        "id3v2": True,
        "ieeefloat": True,
        "layer1": True,
        "layer2": True,
        "layer3": True,
        "moreinfo": True,
        "seektable": "1000",
        "module": "dummy",
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _audio_module(self):
        return {
            "libalsa": "alsa",
        }.get(str(self.options.module), str(self.options.module))

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        if is_msvc(self):
            cmake_layout(self, src_folder="src")
        else:
            basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.module == "libalsa":
            self.requires("libalsa/1.2.10")
        if self.options.module == "tinyalsa":
            self.requires("tinyalsa/2.0.0")

    def validate(self):
        if not str(self.options.seektable).isdigit():
            raise ConanInvalidConfiguration(f"The option -o {self.ref.name}:seektable must be an integer number.")
        if self.settings.os != "Windows" and self.options.module == "win32":
            raise ConanInvalidConfiguration(f"The option -o {self.ref.name}:module should not use 'win32' for non-Windows OS")


    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.0.3")
        if self.settings.arch in ["x86", "x86_64"]:
            self.tool_requires("yasm/1.3.0")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)


    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        if is_msvc(self):
            tc = CMakeToolchain(self)
            tc.variables["NO_MOREINFO"] = not self.options.moreinfo
            tc.variables["NETWORK"] = self.options.network
            tc.variables["NO_NTOM"] = not self.options.flexible_resampling
            tc.variables["NO_ICY"] = not self.options.icy
            tc.variables["NO_ID3V2"] = not self.options.id3v2
            tc.variables["IEEE_FLOAT"] = self.options.ieeefloat
            tc.variables["NO_LAYER1"] = not self.options.layer1
            tc.variables["NO_LAYER2"] = not self.options.layer2
            tc.variables["NO_LAYER3"] = not self.options.layer3
            tc.variables["USE_MODULES"] = False
            tc.variables["CHECK_MODULES"] = self._audio_module
            tc.variables["WITH_SEEKTABLE"] = self.options.seektable
            tc.generate()
            tc = CMakeDeps(self)
            tc.generate()
        else:
            yes_no = lambda v: "yes" if v else "no"
            tc = AutotoolsToolchain(self)
            tc.configure_args.extend([
                f"--enable-moreinfo={yes_no(self.options.moreinfo)}",
                f"--enable-network={yes_no(self.options.network)}",
                f"--enable-ntom={yes_no(self.options.flexible_resampling)}",
                f"--enable-icy={yes_no(self.options.icy)}",
                f"--enable-id3v2={yes_no(self.options.id3v2)}",
                f"--enable-ieeefloat={yes_no(self.options.ieeefloat)}",
                f"--enable-layer1={yes_no(self.options.layer1)}",
                f"--enable-layer2={yes_no(self.options.layer2)}",
                f"--enable-layer3={yes_no(self.options.layer3)}",
                f"--with-audio={self._audio_module}",
                f"--with-default-audio={self._audio_module}",
                f"--with-seektable={self.options.seektable}",
                f"--enable-modules=no",
                f"--enable-shared={yes_no(self.options.shared)}",
                f"--enable-static={yes_no(not self.options.shared)}",
            ])
            if is_apple_os(self):
                # Needed for fix_apple_shared_install_name invocation in package method
                tc.extra_cflags += ["-headerpad_max_install_names"]
            # The finite-math-only optimization has no effect and will cause linking errors
            # when linked against glibc >= 2.31
            tc.extra_cflags += ["-fno-finite-math-only"]
            tc.generate()
            tc = AutotoolsDeps(self)
            tc.generate()

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            cmake = CMake(self)
            cmake.configure(build_script_folder=os.path.join(self.source_folder, "ports", "cmake"))
            cmake.build()
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        else:
            autotools = Autotools(self)
            autotools.install()
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "mpg123")

        self.cpp_info.components["libmpg123"].libs = ["mpg123"]
        self.cpp_info.components["libmpg123"].set_property("pkg_config_name", "libmpg123")
        self.cpp_info.components["libmpg123"].set_property("cmake_target_name", "MPG123::libmpg123")
        self.cpp_info.components["libmpg123"].names["cmake_find_package"] = "libmpg123"
        self.cpp_info.components["libmpg123"].names["cmake_find_package_multi"] = "libmpg123"
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.components["libmpg123"].defines.append("LINK_MPG123_DLL")

        self.cpp_info.components["libout123"].libs = ["out123"]
        self.cpp_info.components["libout123"].set_property("pkg_config_name", "libout123")
        self.cpp_info.components["libout123"].set_property("cmake_target_name", "MPG123::libout123")
        self.cpp_info.components["libout123"].names["cmake_find_package"] = "libout123"
        self.cpp_info.components["libout123"].names["cmake_find_package_multi"] = "libout123"
        self.cpp_info.components["libout123"].requires = ["libmpg123"]

        self.cpp_info.components["libsyn123"].libs = ["syn123"]
        self.cpp_info.components["libsyn123"].set_property("pkg_config_name", "libsyn123")
        self.cpp_info.components["libsyn123"].set_property("cmake_target_name", "MPG123::libsyn123")
        self.cpp_info.components["libsyn123"].names["cmake_find_package"] = "libsyn123"
        self.cpp_info.components["libsyn123"].names["cmake_find_package_multi"] = "libsyn123"
        self.cpp_info.components["libsyn123"].requires = ["libmpg123"]

        if self.settings.os == "Linux":
            self.cpp_info.components["libmpg123"].system_libs = ["m"]
            if self.settings.arch in ["x86", "x86_64"]:
                self.cpp_info.components["libsyn123"].system_libs = ["mvec"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["libmpg123"].system_libs = ["shlwapi"]

        if self.options.module == "libalsa":
            self.cpp_info.components["libout123"].requires.append("libalsa::libalsa")
        if self.options.module == "tinyalsa":
            self.cpp_info.components["libout123"].requires.append("tinyalsa::tinyalsa")
        if self.options.module == "win32":
            self.cpp_info.components["libout123"].system_libs.append("winmm")


        # TODO: Remove after Conan 2.x becomes the standard
        self.cpp_info.filenames["cmake_find_package"] = "mpg123"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mpg123"
        self.cpp_info.names["cmake_find_package"] = "MPG123"
        self.cpp_info.names["cmake_find_package_multi"] = "MPG123"

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
