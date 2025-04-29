from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.env import Environment
from conan.tools.files import get, copy, rmdir, save, collect_libs
from conan.tools.layout import basic_layout
from conan.tools.microsoft import MSBuild, msvs_toolset, is_msvc_static_runtime
from conan.internal.model.cpp_info import CppInfo

import os
import subprocess


required_conan_version = ">=2.0.9"

_BOOL_STR = {
    True: "1",
    False: "0",
}


class DocACEConan(ConanFile):
    """Recipe for ACE + TAO C++ CORBA framework and ORB. Following instructions from
    https://github.com/DOCGroup/ACE_TAO/blob/master/TAO/TAO-INSTALL.html
    """

    name = "ace-tao"
    description = """ACE is a C++ framework for implementing distributed and networked applications,
TAO is a C++ implementation of the OMG's CORBA standard.
"""
    license = "DocumentRef-README:LicenseRef-ACE_TAO"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/DOCGroup/ACE_TAO"
    topics = "corba"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    # See file wrapper_macros.GNU in upstream source for all options
    options = {
        "shared": [True, False],
        "debug": [True, False],
        "lto": [True, False],
        "with_ace_for_tao": [True, False],
        "with_openssl": [True, False],
        "with_optimize": [True, False],
        "with_probe": [True, False],
        "with_profile": [True, False],
        "with_threads": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "shared": False,
        "debug": False,
        "lto": False,
        "with_ace_for_tao": False,
        "with_openssl": True,
        "with_optimize": True,
        "with_probe": False,
        "with_profile": False,
        "with_threads": True,
        "with_zlib": True,
    }

    implements = ["auto_shared_fpic"]

    def export_sources(self):
        pass

    def source(self):
        if self.conan_data["sources"].get(self.version) is None:
            raise ConanInvalidConfiguration(
                f"{self} does not have sources for version {self.version}."
            )

        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def configure(self):
        pass

    def layout(self):
        basic_layout(self, src_folder="ACE_wrappers")

    def requirements(self):
        # See whitelisted ranges there:
        # https://github.com/conan-io/conan-center-index/blob/master/docs/adding_packages/dependencies.md#version-ranges
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")

    def _has_perl(self) -> bool:
        if self.settings.os == "Linux":
            result = subprocess.run(
                ["which", "perl"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            return result.returncode == 0
        return True

    def validate_build(self):
        if not self._has_perl():
            raise ConanInvalidConfiguration(
                "ACE+TAO requires perl to be installed in the system. Please install it and try again."
            )

    def validate(self):
        check_min_cppstd(self, 17)
        # INFO: I have no access to other systems than linux to develop this
        # please submit PRs if you want this to build/work on other OSes
        if self.settings.os == "Linux":
            # If compiler is GCC, check if version is >= 4.8
            if self.settings.compiler == "gcc":
                self.output.info(f"compiler.version: {self.settings.compiler.version}")
                if Version(self.settings.compiler.version) < Version("4.8"):
                    raise ConanInvalidConfiguration(f"{self} requires GCC >= 4.8.")

        if self.settings.os not in ["Linux", "Windows"]:
            raise ConanInvalidConfiguration(
                f"{self} is not supported on {self.settings.os}."
            )

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.tool_requires("strawberryperl/5.32.1.1")

    @property
    def _ace_root(self):
        return self.source_folder

    @property
    def _tao_root(self):
        return os.path.join(self._ace_root, "TAO")

    @property
    def _msvc_toolset_version(self) -> str | None:
        if self.settings.os != "Windows":
            return None
        return msvs_toolset(self)

    def generate(self):
        ace_platforms = {
            "Linux": "linux",
            "Windows": "windows",
        }
        ace_gnu_platforms = {
            "Linux": "linux",
            "Windows": "win32_msvc",
        }

        env = Environment()

        env.define("ACE_ROOT", self._ace_root)
        env.define("TAO_ROOT", self._tao_root)
        env.define("INSTALL_PREFIX", self.package_folder)

        if self.options.with_openssl:
            openssl_info: CppInfo = self.dependencies.get("openssl").cpp_info
            assert openssl_info is not None
            env.define("SSL_ROOT", self.dependencies["openssl"].package_folder)

        if self.options.with_zlib:
            zlib_info: CppInfo = self.dependencies.get("zlib").cpp_info
            assert zlib_info is not None
            env.define("ZLIB_ROOT", self.dependencies["zlib"].package_folder)

        envvars = env.vars(self)
        self.output.info(f"my_env_file will contain: {envvars.items()}")
        envvars.save_script("my_env_file")

        # Create a config file
        ace_platform = ace_platforms[str(self.settings.os)]
        ace_gnu_platform = ace_gnu_platforms[str(self.settings.os)]
        config_path = os.path.join(self._ace_root, "ace", "config.h")
        save(self, config_path, f'#include "ace/config-{ace_platform}.h"\n')

        # Create the makefile parameters
        build_conf_path = os.path.join(
            self._ace_root, "include", "makeinclude", "platform_macros.GNU"
        )
        # see wrapper_macros.GNU for all options

        debug = bool(self.options.debug) or (self.settings.build_type == "Debug")
        build_config = (
            f"shared_libs={_BOOL_STR[bool(self.options.shared)]}\n"
            f"ace_for_tao={_BOOL_STR[bool(self.options.with_ace_for_tao)]}\n"
            f"static_libs={_BOOL_STR[not bool(self.options.shared)]}\n"
            f"threads={_BOOL_STR[bool(self.options.with_threads)]}\n"
            f"debug={_BOOL_STR[debug]}\n"
            f"optimize={_BOOL_STR[bool(self.options.with_optimize)]}\n"
            f"probe={_BOOL_STR[bool(self.options.with_probe)]}\n"
            f"profile={_BOOL_STR[bool(self.options.with_profile)]}\n"
            f"ssl={_BOOL_STR[bool(self.options.with_openssl)]}\n"
            f"include $(ACE_ROOT)/include/makeinclude/platform_{ace_gnu_platform}.GNU\n"
        )

        self.output.info(f"{build_conf_path} will be: {build_config}")
        save(self, build_conf_path, build_config)

    def build(self):
        mcw_path = os.path.join(self._ace_root, "bin", "mwc.pl")
        tao_mwc_path = os.path.join("TAO", "TAO_ACE.mwc")

        ace_mvsc_build_type = {
            "v140": "vs2015",
            "v141": "vs2017",
            "v142": "vs2019",
            "v143": "vs2022",
        }

        build_type = (
            ace_mvsc_build_type[self._msvc_toolset_version]
            if self._msvc_toolset_version
            else "gnuace"
        )

        self.output.highlight(f"Building build files of type {build_type}")

        command = (
            f"perl {mcw_path} "
            + f"{tao_mwc_path} -type {build_type} "
            + f"-features zlib={_BOOL_STR[bool(self.options.with_zlib)]},"
            + f"ssl={_BOOL_STR[bool(self.options.with_openssl)]},"
            + f"ace_for_tao={_BOOL_STR[bool(self.options.with_ace_for_tao)]} "
            + f"-workers {os.cpu_count()} "
            + (" -static " if not self.options.shared else "")
        )

        if self.settings.os == "Windows":
            lto_str = "true " if self.options.lto else "false "
            debug_str = "Debug" if self.settings.build_type == "Debug" else ""
            dll_str = "" if is_msvc_static_runtime(self) else "DLL"
            command += (
                "-value_template linktimecodegeneration=UseLinkTimeCodeGeneration "
                if self.options.lto
                else ""
            )
            command += f"-value_template wholeprogramoptimization={lto_str} "
            command += (
                f"-value_template runtime_library=MultiThreaded{debug_str}{dll_str} "
            )
            command += "-value_template MultiProcessorCompilation=true "
            command += f"-value_template CL_MPCount={os.cpu_count()} "

        self.run(command, cwd=self.source_folder)

        if self.settings.os == "Linux":
            self.output.highlight("Making ACE")
            self.run(f"make -j {os.cpu_count()}", cwd=self.source_folder)
            self.output.highlight("Making TAO")
            self.run(
                f"make -j {os.cpu_count()}", cwd=os.path.join(self.source_folder, "TAO")
            )

        if self.settings.os == "Windows":
            builder = MSBuild(self)
            builder.build(
                os.path.join(self._tao_root, "TAO_ACE.sln"),
                targets=[
                    "TAO",
                    "CosNaming",
                    "TAO_Utils",
                    "Messaging",
                    "AnyTypeCode",
                    "RTCORBA",
                ],
            )

    def package(self):
        if self.settings.os == "Windows":

            def mycopy(pattern, d):
                copy(
                    self,
                    pattern,
                    src=self.source_folder,
                    dst=os.path.join(self.package_folder, d),
                )

            self.output.info(
                "Copying files manually, as there is no make install on Windows"
            )
            mycopy("bin/*.exe", "")
            mycopy("bin/*.pdb", "")
            mycopy("lib/*.dll", "")
            mycopy("lib/*.lib", "")
            mycopy("lib/*.pdb", "")

            for ext in ["*.h", "*.cpp", "*.inl", "*.idl", "*.pidl"]:

                def mycopy(pattern, src, dst):
                    copy(
                        self,
                        pattern,
                        src=os.path.join(self._ace_root, src),
                        dst=os.path.join(self.package_folder, dst),
                    )

                mycopy(ext, "ace", "include/ace")
                mycopy(ext, "ACEXML", "include/ACEXML")
                mycopy(ext, "Kokyu", "include/Kokyu")
                mycopy(ext, "TAO/orbsvcs/orbsvcs", "include/orbsvcs")
                mycopy(ext, "TAO/tao", "include/tao")

        if self.settings.os == "Linux":
            self.run(
                "make install",
                cwd=os.path.join(self.source_folder),
            )
            self.run(
                "make install",
                cwd=os.path.join(self.source_folder, "TAO"),
            )

        # Remove unnecessary files
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "include", "ACEXML", "examples"))
        rmdir(self, os.path.join(self.package_folder, "include", "ACEXML", "tests"))
        rmdir(self, os.path.join(self.package_folder, "include", "Kokyu", "tests"))

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.output.info(f"libs: {self.cpp_info.libs}")

        # In case you consume ace headers
        self.cpp_info.defines.append("ACE_HAS_CPP17")

        if self.options.with_ace_for_tao:
            self.cpp_info.defines.append("ACE_LACKS_ACE_TOKEN")

        if not self.options.shared:
            self.cpp_info.defines.append("ACE_AS_STATIC_LIBS")
            self.cpp_info.defines.append("TAO_AS_STATIC_LIBS")

        if self.options.with_threads:
            threads_lib = "Iphlpapi" if self.settings.os == "Windows" else "pthread"
            self.cpp_info.system_libs.extend([threads_lib])

        if self.settings.os == "Windows":
            # So consumer can find the DLLs
            lib_path = os.path.join(self.package_folder, "lib")
            self.runenv_info.prepend_path("PATH", lib_path)
