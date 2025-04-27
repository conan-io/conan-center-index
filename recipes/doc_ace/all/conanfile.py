from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.env import Environment
from conan.tools.files import get, save
from conan.tools.layout import basic_layout
from conan.internal.model.cpp_info import CppInfo

import os


required_conan_version = ">=2.0.9"


class DocACEConan(ConanFile):
    """Recipe for ACE C++ framework. Following instructions from
    https://github.com/DOCGroup/ACE_TAO/blob/master/ACE/ACE-INSTALL.html
    """
    name = "doc_ace"
    description = """See Douglas C. Schmidt website for more information about ACE/TAO.
The quality of ACE/TAO is monitored through our distributed scoreboard
ACE is a C++ framework for implementing distributed and networked applications,
TAO is a C++ implementation of the OMG's CORBA standard.
"""
    license = "DocumentRef-README:LicenseRef-ACE_TAO"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/DOCGroup/ACE_TAO"
    topics = ("corba")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    
    # See file wrapper_macros.GNU in upstream source for all options
    options = {
        "shared": [True, False],
        "debug": [True, False],
        "with_openssl": [True, False],
        "with_optimize": [True, False],
        "with_probe": [True, False],
        "with_profile": [True, False],
        "with_threads": [True, False],
    }
    default_options = {
        "shared": False,
        "debug": False,
        "with_openssl": False,
        "with_optimize": True,
        "with_probe": False,
        "with_profile": False,
        "with_threads": True,
    }

    implements = ["auto_shared_fpic"]

    def export_sources(self):
        pass

    def configure(self):
        pass

    def layout(self):
        basic_layout(self, src_folder="ACE_wrappers")

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")


    def validate(self):
        check_min_cppstd(self, 14)
        # INFO: I have no access to other systems than linux to develop this
        # please submit PRs if you want this to build/work on other OSes
        if self.settings.os == "Linux":
            # If compiler is GCC, check if version is >= 4.8
            if self.settings.compiler == "gcc":
                self.output.info(f"compiler.version: {self.settings.compiler.version}")
                if Version(self.settings.compiler.version) < Version("4.8"):
                    raise ConanInvalidConfiguration(f"{self} requires GCC >= 4.8.")

        if self.settings.os not in ["Linux"]:
            raise ConanInvalidConfiguration(f"{self} is not supported on {self.settings.os}.")

    def build_requirements(self):
        pass

    def source(self):
        if self.conan_data["sources"].get(self.version) is None:
            raise ConanInvalidConfiguration(f"{self} does not have sources for version {self.version}.")
        
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        ace_platforms = {
            "Linux": "linux",
        }
        _bool_str = {
            True: "1",
            False: "0",
        }
        env = Environment()
        ace_root = self.source_folder
        self.output.info(f"ACE_ROOT: {ace_root}")
        self.output.info(f"INSTALL_PREFIX: {self.package_folder}")

        env.define("ACE_ROOT", ace_root)
        env.define("INSTALL_PREFIX", self.package_folder)

        cflags_str = ""
        lflags_str = ""

        if self.options.with_openssl:
            openssl_info: CppInfo = self.dependencies.get("openssl").cpp_info
            if openssl_info is None:
                raise ConanInvalidConfiguration("openssl not found in dependencies")
            cflags_str += " ".join([f"-I{d}" for d in openssl_info.includedirs])
            lflags_str += " ".join([f"-L{d}" for d in openssl_info.libdirs])


        self.output.debug("CCFLAGS: {cflags_str}")
        env.define("CCFLAGS", cflags_str)

        self.output.debug(f"LDFLAGS: {lflags_str}")
        env.define("LDFLAGS", lflags_str)

        envvars = env.vars(self)
        envvars.save_script("my_env_file")

        # Create a config file
        ace_platform = ace_platforms[str(self.settings.os)]
        config_path = os.path.join(ace_root, "ace", "config.h")
        save(self, config_path, f"#include \"ace/config-{ace_platform}.h\"\n")

        # Create the makefile parameters
        build_conf_path = os.path.join(ace_root, "include", "makeinclude" , "platform_macros.GNU")
        # see wrapper_macros.GNU for all options
        save(self, build_conf_path,
             f"shared_lib={_bool_str[bool(self.options.shared)]}\n"
             f"static_libs={_bool_str[not bool(self.options.shared)]}\n"
             f"threads={_bool_str[bool(self.options.with_threads)]}\n"
             f"debug={_bool_str[bool(self.options.debug) or self.settings.build_type == "Debug"]}\n"
             f"optimize={_bool_str[bool(self.options.with_optimize)]}\n"
             f"probe={_bool_str[bool(self.options.with_probe)]}\n"
             f"profile={_bool_str[bool(self.options.with_profile)]}\n"
             f"ssl={_bool_str[bool(self.options.with_openssl)]}\n"
             f"include $(ACE_ROOT)/include/makeinclude/platform_{ace_platform}.GNU\n")



    def build(self):     
        just_ace = os.path.join(self.source_folder, "ace")
        self.output.info("Calling make")
        self.run("make -j 4", cwd=just_ace, env=["my_env_file"])

    def package(self):
        self.run("make install", cwd=os.path.join(self.source_folder, "ace"), env=["my_env_file"])

        # Some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        # rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        # Consider disabling these at first to verify that the package_info() output matches the info exported by the project.
        #rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        #rmdir(self, os.path.join(self.package_folder, "share"))

        # In shared lib/executable files, autotools set install_name (macOS) to lib dir absolute path instead of @rpath, it's not relocatable, so fix it
        # fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["ACE", "ACE_ETCL", "ACE_ETCL_Parser", "ACE_Monitor_Control"]#
        if self.options.with_openssl:
            self.cpp_info.libs.extend(["ACE_SSL"])

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl","m"])

        if self.options.with_threads:
            self.cpp_info.system_libs.extend(["pthread"])
