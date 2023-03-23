from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.53.0"


class OdbcConan(ConanFile):
    name = "odbc"
    package_type = "library"
    description = "Package providing unixODBC"
    topics = ("odbc", "database", "dbms", "data-access")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.unixodbc.org"
    license = ("LGPL-2.1", "GPL-2.1")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libiconv": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libiconv": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libtool/2.4.7")
        if self.options.with_libiconv:
            self.requires("libiconv/1.17")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("odbc is a system lib on Windows")

    def build_requirements(self):
        self.tool_requires("gnu-config/cci.20210814")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        libtool_cppinfo = self.dependencies["libtool"].cpp_info.aggregated_components()
        tc.configure_args.extend([
            "--without-included-ltdl",
            f"--with-ltdl-include={libtool_cppinfo.includedirs[0]}",
            f"--with-ltdl-lib={libtool_cppinfo.libdirs[0]}",
            "--disable-ltdl-install",
            f"--enable-iconv={yes_no(self.options.with_libiconv)}",
            "--sysconfdir=/etc",
        ])
        if self.options.with_libiconv:
            libiconv_prefix = self.dependencies["libiconv"].package_folder
            tc.configure_args.append(f"--with-libiconv-prefix={libiconv_prefix}")
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # support more triplets
        for gnu_config in [
            self.conf.get("user.gnu-config:config_guess", check_type=str),
            self.conf.get("user.gnu-config:config_sub", check_type=str),
        ]:
            if gnu_config:
                copy(self, os.path.basename(gnu_config), src=os.path.dirname(gnu_config), dst=self.source_folder)
        # allow external libtdl (in libtool recipe)
        replace_in_file(
            self,
            os.path.join(self.source_folder, "configure"),
            "if test -f \"$with_ltdl_lib/libltdl.la\";",
            "if true;",
        )
        libtool_system_libs = self.dependencies["libtool"].cpp_info.aggregated_components().system_libs
        if libtool_system_libs:
            replace_in_file(
                self,
                os.path.join(self.source_folder, "configure"),
                "-L$with_ltdl_lib -lltdl",
                "-L$with_ltdl_lib -lltdl -l{}".format(" -l".join(libtool_system_libs)),
            )

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "etc"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "ODBC")
        self.cpp_info.set_property("cmake_target_name", "ODBC::ODBC")
        # to avoid conflict with pkgconfig file of _odbc component
        self.cpp_info.set_property("pkg_config_name", "odbc_full_package")

        self.cpp_info.names["cmake_find_package"] = "ODBC"
        self.cpp_info.names["cmake_find_package_multi"] = "ODBC"

        # odbc
        self.cpp_info.components["_odbc"].set_property("pkg_config_name", "odbc")
        self.cpp_info.components["_odbc"].libs = ["odbc"]
        self.cpp_info.components["_odbc"].requires = ["libtool::libtool"]
        if self.options.with_libiconv:
            self.cpp_info.components["_odbc"].requires.append("libiconv::libiconv")

        # odbcinst
        self.cpp_info.components["odbcinst"].set_property("pkg_config_name", "odbcinst")
        self.cpp_info.components["odbcinst"].libs = ["odbcinst"]
        self.cpp_info.components["odbcinst"].requires = ["libtool::libtool"]

        # odbccr
        self.cpp_info.components["odbccr"].set_property("pkg_config_name", "odbccr")
        self.cpp_info.components["odbccr"].libs = ["odbccr"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_odbc"].system_libs = ["pthread"]
            self.cpp_info.components["odbcinst"].system_libs = ["pthread"]

        # TODO: to remove in conan v2
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
