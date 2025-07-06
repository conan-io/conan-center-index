from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import copy, get, rm, rmdir, export_conandata_patches, apply_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.0.9"


class Log4cppConan(ConanFile):
    name = "log4cpp"
    description = (
        "A library of C++ classes for flexible logging to files (rolling), syslog, "
        "IDSA and other destinations. It is modeled after the Log4j Java library, "
        "staying as close to their API as is reasonable."
    )
    license = "LGPL-2.1-or-later"
    topics = ("logging", "log", "logging-library")
    homepage = "https://log4cpp.sourceforge.net/"
    url = "https://github.com/conan-io/conan-center-index"
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

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(
                f"{self.ref} recipe doesn't support Windows yet, but it could. Contributions are welcomed."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            "--enable-debug={}".format(yes_no(self.settings.build_type == "Debug")),
            # Always use system snprintf instead of internal one
            "ac_cv_func_snprintf=yes",
        ])
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure(build_script_folder=os.path.join(self.source_folder, "log4cpp"))
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=os.path.join(self.source_folder, "log4cpp"), dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "log4cpp")
        self.cpp_info.libs = ["log4cpp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
