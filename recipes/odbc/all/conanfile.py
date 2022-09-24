from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
import os
import shutil

required_conan_version = ">=1.52.0"


class OdbcConan(ConanFile):
    name = "odbc"
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

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libtool/2.4.7")
        if self.options.with_libiconv:
            self.requires("libiconv/1.17")

    def validate(self):
        if self.info.settings.os == "Windows":
            raise ConanInvalidConfiguration("odbc is a system lib on Windows")

    def build_requirements(self):
        self.tool_requires("gnu-config/cci.20210814")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            "--without-included-ltdl",
            f"--with-ltdl-include={self.dependencies['libtool'].cpp_info.includedirs[0]}",
            f"--with-ltdl-lib={self.dependencies['libtool'].cpp_info.libdirs[0]}",
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
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self.source_folder, "config.sub"))
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self.source_folder, "config.guess"))
        # allow external libtdl (in libtool recipe)
        replace_in_file(
            self,
            os.path.join(self.source_folder, "configure"),
            "if test -f \"$with_ltdl_lib/libltdl.la\";",
            "if true;",
        )
        libtool_system_libs = self.dependencies["libtool"].cpp_info.system_libs
        if libtool_system_libs:
            replace_in_file(
                self,
                os.path.join(self.source_folder, "configure"),
                "-L$with_ltdl_lib -lltdl",
                "-L$with_ltdl_lib -lltdl -l{}".format(" -l".join(libtool_system_libs)),
            )
        # relocatable shared libs on macOS
        for configure in [
            os.path.join(self.source_folder, "configure"),
            os.path.join(self.source_folder, "libltdl", "configure"),
        ]:
            replace_in_file(self, configure, "-install_name \\$rpath/", "-install_name @rpath/")

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
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)
