from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import chdir, copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import glob
import os
import shutil

required_conan_version = ">=1.53.0"


class LibPcapConan(ConanFile):
    name = "libpcap"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/the-tcpdump-group/libpcap"
    description = "libpcap is an API for capturing network traffic"
    license = "BSD-3-Clause"
    topics = ("networking", "pcap", "sniffing", "network-traffic")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_dbus": [True, False],
        "enable_libnl": [True, False],
        "enable_libusb": [True, False],
        "enable_rdma": [True, False],
        "with_snf": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_dbus": False,
        "enable_libnl": False,
        "enable_libusb": False,
        "enable_rdma": False,
        "with_snf": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.enable_libusb
            del self.options.enable_libnl
            del self.options.enable_rdma

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        if self.settings.os == "Windows":
            cmake_layout(self, src_folder="src")
        else:
            basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("enable_libusb"):
            self.requires("libusb/1.0.26")
        if self.options.get_safe("enable_libnl"):
            self.requires("libnl/3.8.0")
        if self.options.get_safe("enable_rdma"):
            self.requires("rdma-core/52.0")
        if self.options.get_safe("enable_dbus"):
            self.requires("dbus/1.15.8")
        # TODO: Add libbluetooth when available

    def build_requirements(self):
        if self.settings_build.os == "Windows":
            self.tool_requires("winflexbison/2.5.25")
        else:
            self.tool_requires("bison/3.8.2")
            self.tool_requires("flex/2.6.4")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()

        if self.settings.os == "Windows":
            tc = CMakeToolchain(self)
            if not self.options.shared:
                tc.variables["ENABLE_REMOTE"] = False
            if is_msvc(self):
                tc.variables["USE_STATIC_RT"] = is_msvc_static_runtime(self)
            else:
                # Don't force -static-libgcc for MinGW, because conan users expect
                # to inject this compilation flag themselves
                tc.variables["USE_STATIC_RT"] = False
            tc.cache_variables["DISABLE_DPDK"] = True

            if Version(self.version) >= "1.10.5":
                self.output.warning("PCAP on Windows is currently built with package capture capabilities - only support is for reading/writing capture files")
                tc.cache_variables["PCAP_TYPE"] = "null"
            tc.generate()
        else:
            if not cross_building(self):
                VirtualRunEnv(self).generate(scope="build")

            tc = AutotoolsToolchain(self)
            yes_no = lambda v: "yes" if v else "no"
            tc.configure_args.extend([
                "--disable-universal",  # don't build universal binaries on macOS
                "--enable-usb" if self.options.get_safe("enable_libusb") else "--disable-usb",
                "--enable-dbus" if self.options.get_safe("enable_dbus") else "--disable-dbus",
                "--enable-rdma" if self.options.get_safe("enable_rdma") else "--disable-rdma",
                "--with-libnl" if self.options.get_safe("enable_libnl") else "--without-libnl",
                "--disable-bluetooth",
                f"--with-snf={yes_no(self.options.get_safe('with_snf'))}",
            ])
            tc.configure_args.append("--disable-packet-ring")
            tc.configure_args.append("--without-dpdk")
            if cross_building(self):
                target_os = "linux" if self.settings.os in ["Linux", "Android"] else "null"
                tc.configure_args.append(f"--with-pcap={target_os}")
            elif "arm" in self.settings.arch and self.settings.os == "Linux":
                tc.configure_args.append("--host=arm-linux")
            tc.generate()

            AutotoolsDeps(self).generate()
            deps = PkgConfigDeps(self)
            deps.generate()

    def build(self):
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.install()

            def flatten_filetree(folder):
                for file in glob.glob(folder + "/**/*"):
                    shutil.move(file, folder + os.sep)
                for subdir in [dir[0] for dir in os.walk(folder) if dir[0] != folder]:
                    os.rmdir(subdir)

            # libpcap installs into a subfolder like x64 or amd64
            with chdir(self, self.package_folder):
                flatten_filetree("bin")
                flatten_filetree("lib")

            rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
            if self.options.shared:
                rm(self, "pcap_static.lib", os.path.join(self.package_folder, "lib"))
                rm(self, "libpcap.a", os.path.join(self.package_folder, "lib"))
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "bin"))
            rmdir(self, os.path.join(self.package_folder, "share"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            if self.options.shared:
                rm(self, "*.a", os.path.join(self.package_folder, "lib"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libpcap")
        suffix = "_static" if self.settings.os == "Windows" and not self.options.shared else ""
        self.cpp_info.libs = [f"pcap{suffix}"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
        if self.options.get_safe("enable_libusb"):
            self.cpp_info.requires.append("libusb::libusb")
        if self.options.get_safe("enable_libnl"):
            self.cpp_info.requires.append("libnl::nl-genl")
        if self.options.get_safe("enable_rdma"):
            self.cpp_info.requires.append("rdma-core::libibverbs")
        if self.options.get_safe("enable_dbus"):
            self.cpp_info.requires.append("dbus::dbus")
        if self.options.get_safe("with_snf"):
            self.cpp_info.system_libs.append("snf")
