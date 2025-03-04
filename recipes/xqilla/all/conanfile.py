from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd, cross_building, valid_min_cppstd
from conan.tools.env import VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, load, rename, rm, save
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
import os

required_conan_version = ">=2.0.9"


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
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("xerces-c/3.2.5", transitive_headers=True, transitive_libs=True)

    def validate(self):
        check_min_cppstd(self, 11)
        if is_msvc(self):
            raise ConanInvalidConfiguration("xqilla recipe doesn't support msvc build yet")

    def build_requirements(self):
        self.tool_requires("gnu-config/cci.20210814")
        self.tool_requires("libtool/2.4.7")
        if self.settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        tc.configure_args.append(f"--with-xerces={unix_path(self, self.dependencies['xerces-c'].package_folder)}")
        if not valid_min_cppstd(self, self._min_cppstd):
            tc.extra_cxxflags.append(f"-std=c++{self._min_cppstd}")
        # warning: ISO C++17 does not allow 'register' storage class specifier
        tc.extra_defines.append("register=")
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

    def _patch_sources(self):
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
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["xqilla"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
