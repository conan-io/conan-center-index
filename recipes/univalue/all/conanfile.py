from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class UnivalueConan(ConanFile):
    name = "univalue"
    description = "High performance RAII C++ JSON library and universal value object class"
    topics = ("universal", "json", "encoding", "decoding")
    license = "MIT"
    homepage = "https://github.com/jgarzik/univalue"
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

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        if is_msvc(self):
            tc.extra_cxxflags.append("-EHsc")
            if (self.settings.compiler == "Visual Studio" and Version(self.settings.compiler.version) >= "12") or \
               (self.settings.compiler == "msvc" and Version(self.settings.compiler.version) >= "180"):
                tc.extra_cflags.append("-FS")
                tc.extra_cxxflags.append("-FS")
        tc.generate()

        if is_msvc(self):
            env = Environment()
            ar_wrapper = unix_path(self, self._user_info_build["automake"].ar_lib)
            env.define("CC", "cl -nologo")
            env.define("CXX", "cl -nologo")
            env.define("CPP", "cl -nologo -EP")
            env.define("LD", "link -nologo")
            env.define("CXXLD", "link -nologo")
            env.define("AR", f"{ar_wrapper} \"lib -nologo\"")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_univalue_msvc")

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        if is_msvc(self):
            replace_in_file(
                self,
                os.path.join(self.build_folder, "libtool"),
                "-Wl,-DLL,-IMPLIB",
                "-link -DLL -link -DLL -link -IMPLIB",
            )
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        # TODO: replace by autotools.install() once https://github.com/conan-io/conan/issues/12153 fixed
        autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        if is_msvc(self) and self.options.shared:
            rename(self, os.path.join(self.package_folder, "lib", "univalue.dll.lib"),
                         os.path.join(self.package_folder, "lib", "univalue.lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libunivalue")
        self.cpp_info.libs = ["univalue"]
        if self.options.shared:
            self.cpp_info.defines = ["UNIVALUE_SHARED"]
