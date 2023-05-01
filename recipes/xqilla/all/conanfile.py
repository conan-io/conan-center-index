from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd, cross_building, valid_min_cppstd
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, load, rename, rm, save
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
import os

required_conan_version = ">=1.53.0"


class XqillaConan(ConanFile):
    name = "xqilla"
    description = (
        "XQilla is an XQuery and XPath 2 library and command line utility "
        "written in C++, implemented on top of the Xerces-C library"
    )
    topics = ("xml", "xquery")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://xqilla.sourceforge.net/HomePage"
    license = "Apache-2.0"
    package_type = "library"
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
    def _min_cppstd(self):
        return "11"

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

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("xerces-c/3.2.3")

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        if is_msvc(self):
            raise ConanInvalidConfiguration("xqilla recipe doesn't support msvc build yet")

    def build_requirements(self):
        self.tool_requires("gnu-config/cci.20210814")
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
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        tc.configure_args.append(f"--with-xerces={unix_path(self, self.dependencies['xerces-c'].package_folder)}")
        if not valid_min_cppstd(self, self._min_cppstd):
            tc.extra_cxxflags.append(f"-std=c++{self._min_cppstd}")
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        for gnu_config in [
            self.conf.get("user.gnu-config:config_guess", check_type=str),
            self.conf.get("user.gnu-config:config_sub", check_type=str),
        ]:
            if gnu_config:
                copy(self, os.path.basename(gnu_config),
                           src=os.path.dirname(gnu_config),
                           dst=os.path.join(self.source_folder, "autotools"))

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def _extract_yajl_license(self):
        tmp = load(self, os.path.join(self.source_folder, "src", "yajl", "yajl_buf.h"))
        return tmp[2:tmp.find("*/", 1)]

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "README", src=os.path.join(self.source_folder, "src", "mapm"),
                             dst=os.path.join(self.package_folder, "licenses"))
        rename(self, os.path.join(self.package_folder, "licenses", "README"),
                     os.path.join(self.package_folder, "licenses", "LICENSE.mapm"))
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE.yajl"), self._extract_yajl_license())

        autotools = Autotools(self)
        # TODO: replace by autotools.install() once https://github.com/conan-io/conan/issues/12153 fixed
        autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["xqilla"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")

        # TODO: to remove in conan v2
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
