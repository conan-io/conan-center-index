from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import symlinks, rmdir, get, replace_in_file, rename, chdir, patch, mkdir, copy, apply_conandata_patches
from conan.tools.scm import Version
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import MSBuild, is_msvc, MSBuildToolchain, VCVars
import os


required_conan_version = ">=1.53.0"


class MdnsResponderConan(ConanFile):
    name = "mdnsresponder"
    description = "Apple Open Source DNS Service Discovery Collection"
    topics = ("Bonjour", "DNS-SD", "mDNS")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://opensource.apple.com/tarballs/mDNSResponder/"
    license = "Apache-2.0", "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_opt_patches": [True, False],
        "use_tls": [True, False],
        "unicast_disabled": [True, False],
    }
    default_options = {
        "with_opt_patches": False,
        "use_tls": False,
        "unicast_disabled": False,
    }

    def export_sources(self):
        # INFO: export_conandata_patches will not export optional patches
        copy(self, "*.patch", dst=os.path.join(self.export_sources_folder, "patches"), src=os.path.join(self.recipe_folder, "patches"))

    def configure(self):
        if self.options.use_tls:
            #The target(libdns_sd) is a shared lib, so mbedtls enable 'shared' option
            self.options['mbedtls'].shared = True

    def requirements(self):
        if self.options.use_tls:
            self.requires("mbedtls/2.25.0")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os not in ["Linux", "Windows"]:
            raise ConanInvalidConfiguration("Only Linux and Windows are supported for this package.")
        if Version(self.version) >= "1096.0.2":
            # recent tarballs (since 1096.0.2) are missing mDNSWindows, so for now, Linux only
            if self.settings.os == "Windows":
                raise ConanInvalidConfiguration("Windows is not supported for version {}.".format(self.version))
            # TCP_NOTSENT_LOWAT is causing build failures for packages built with gcc 4.9
            # the best check would probably be for Linux kernel v3.12, but for now...
            if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "5":
                raise ConanInvalidConfiguration("Only gcc 5 or higher is supported for this package.")
            # __has_c_attribute is not available in Clang 5
            if self.settings.compiler == "clang" and Version(self.settings.compiler.version) < "6":
                raise ConanInvalidConfiguration("Only Clang 6 or higher is supported for this package.")
        # FIXME: Migration of the project files fails with VS 2017 on c3i (conan-center-index's infrastructure)
        # though works OK with VS 2015 and VS 2019, and works with VS 2017 in my local environment
        if is_msvc(self) and (Version(self.settings.compiler.version) == "15" or "1910" <= Version(self.settings.compiler.version) <= "1916"):
            raise ConanInvalidConfiguration("Visual Studio 2017 is not supported in CCI (yet).")
        if self.options.use_tls and (not self.dependencies["mbedtls"].options.shared):
            raise ConanInvalidConfiguration("The dependency 'mbedtls' must be built as a shared library.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _posix_folder(self):
        return os.path.join(self.source_folder, "mDNSPosix")

    @property
    def _make_build_args(self):
        # the Makefile does not support parallel builds
        build_args = [
            "os=linux",
            "-j1",
        ]
        if not self.options.use_tls:
            build_args.append("tls=no")
        #FIXME: 878.200.35 and 1310.140.1 will fail to compile when DEBUG=1
        if self.settings.build_type == "Debug" and Version(self.version) != "878.200.35" and Version(self.version) != "1310.140.1":
            build_args.append("DEBUG=1")
        if self.options.unicast_disabled:
            build_args.append("unicast_disabled=y")

        return build_args

    @property
    def _make_build_targets(self):
        return " ".join(["setup", "Daemon", "libdns_sd", "Clients"])

    @property
    def _make_install_args(self):
        return self._make_build_args + [
            "INSTBASE={}".format(self.package_folder),
            "STARTUPSCRIPTDIR={}/bin".format(self.package_folder),
            "RUNLEVELSCRIPTSDIR=",
        ]

    @property
    def _make_install_targets(self):
        # not installing man pages, NSS plugin
        return " ".join(["setup", "InstalledDaemon", "InstalledLib", "InstalledClients"])

    def _build_make(self):
        with chdir(self, self._posix_folder):
            autotools = Autotools(self)
            autotools.make(args=self._make_build_args, target=self._make_build_targets)

    @property
    def _msvc_targets(self):
        return ["mDNSResponder", "DLL", "DLLStub", "dns-sd"]

    @property
    def _msvc_definitions(self):
        return {"_WINSOCK_DEPRECATED_NO_WARNINGS": None}

    @property
    def _msvc_platforms(self):
        return {"x86": "Win32", "x86_64": "x64"}

    @property
    def _msvc_platform(self):
        return self._msvc_platforms[str(self.settings.arch)]

    def _build_msvc(self):
        sln = os.path.join(self.source_folder, "mDNSResponder.sln")
        if "MD" in self.settings.compiler.runtime:
            # could use glob and replace_in_file(strict=False, ...)
            dll_vcxproj = os.path.join(self.source_folder, "mDNSWindows", "DLL", "dnssd.vcxproj")
            dllstub_vcxproj = os.path.join(self.source_folder, "mDNSWindows", "DLLStub", "DLLStub.vcxproj")
            dns_sd_vcxproj = os.path.join(self.source_folder, "Clients", "DNS-SD.VisualStudio", "dns-sd.vcxproj")
            for vcxproj in [dll_vcxproj, dllstub_vcxproj, dns_sd_vcxproj]:
                replace_in_file(self, vcxproj, "<RuntimeLibrary>MultiThreaded</RuntimeLibrary>", "<RuntimeLibrary>MultiThreadedDLL</RuntimeLibrary>")
                replace_in_file(self, vcxproj, "<RuntimeLibrary>MultiThreadedDebug</RuntimeLibrary>", "<RuntimeLibrary>MultiThreadedDebugDLL</RuntimeLibrary>")

        # could use glob and replace_in_file(strict=False, ...)
        dll_rc = os.path.join(self.source_folder, "mDNSWindows", "DLL", "dll.rc")
        dns_sd_rc = os.path.join(self.source_folder, "Clients", "DNS-SD.VisualStudio", "dns-sd.rc")
        for rc in [dll_rc, dns_sd_rc]:
            replace_in_file(self, rc, "afxres.h", "winres.h")

        msbuild = MSBuild(self)
        # use Win32 instead of the default value when building x86
        msbuild.platform = "Win32" if self.settings.arch == "x86" else msbuild.platform
        #TODO: How to add _msvc_definitions to msbuild.build
        msbuild.build(sln, targets=self._msvc_targets)

    def generate(self):
        if self.settings.os == "Linux":
            tc = AutotoolsToolchain(self)
            # fix for error: 'for' loop initial declarations are only allowed in C99 or C11 mode
            tc.extra_cflags.append("-std=gnu99")
            tc.generate()
            tc = AutotoolsDeps(self)
            tc.generate()
        elif is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.configuration = "Debug" if self.settings.build_type == "Debug" else "Release"
            tc.generate()
            tc = VCVars(self)
            tc.generate()

    def build(self):
        apply_conandata_patches(self)
        if self.options.with_opt_patches:
            for patchfile in self.conan_data.get("patches", {}).get("{}-opt".format(self.version), []):
                patch(self, **patchfile)
        if self.settings.os == "Linux":
            self._build_make()
        elif self.settings.os == "Windows":
            self._build_msvc()

    def _install_make(self):
        for dir in ["bin", "include", "lib", "sbin"]:
            mkdir(self, os.path.join(self.package_folder, dir))
        with chdir(self, self._posix_folder):
            autotools = Autotools(self)
            autotools.make(args=self._make_install_args, target=self._make_install_targets)
        # package the daemon in bin too
        rename(self, os.path.join(self.package_folder, "sbin", "mdnsd"),
                     os.path.join(self.package_folder, "bin", "mdnsd"))
        rmdir(self, os.path.join(self.package_folder, "sbin"))
        symlinks.absolute_to_relative_symlinks(self, self.package_folder)

    def _msvc_build_folder(self, *argv):
        return os.path.join(self.source_folder, *argv, self._msvc_platform, str(self.settings.build_type))

    def _install_msvc(self):
        copy(self, "mDNSResponder.exe", dst=os.path.join(self.package_folder, "bin"), src=self._msvc_build_folder("mDNSWindows", "SystemService"))
        copy(self, "dns_sd.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "mDNSShared"))
        copy(self, "dnssd.dll", dst=os.path.join(self.package_folder, "bin"), src=self._msvc_build_folder("mDNSWindows", "DLL"))
        copy(self, "dnssdStatic.lib", dst=os.path.join(self.package_folder, "lib"), src=self._msvc_build_folder("mDNSWindows", "DLLStub"))
        # rename consistently with Bonjour SDK
        rename(self, src=os.path.join(self.package_folder, "lib", "dnssdStatic.lib"),
                     dst=os.path.join(self.package_folder, "lib", "dnssd.lib"))
        copy(self, "dns-sd.exe", dst=os.path.join(self.package_folder, "bin"), src=self._msvc_build_folder("Clients", "DNS-SD.VisualStudio"))

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if self.settings.os == "Linux":
            self._install_make()
        elif self.settings.os == "Windows":
            self._install_msvc()

    def package_info(self):
        # although not one of the find-modules in the CMake distribution, FindDNSSD.cmake is commonly used for this package
        self.cpp_info.names["cmake_find_package"] = "DNSSD"
        self.cpp_info.names["cmake_find_package_multi"] = "DNSSD"
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "DNSSD")
        self.cpp_info.set_property("cmake_target_name", "DNSSD::DNSSD")

        if self.settings.os == "Linux":
            self.cpp_info.libs = ["dns_sd"]
        elif self.settings.os == "Windows":
            self.cpp_info.libs = ["dnssd"]

        # add path for daemon (mdnsd, mDNSResponder) and client (dns-sd)
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
