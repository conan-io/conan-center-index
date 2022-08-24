from conan.tools.microsoft import msvc_runtime_flag
from conans import AutoToolsBuildEnvironment, tools, ConanFile, CMake
from conan.errors import ConanInvalidConfiguration
import glob
import os
import shutil

required_conan_version = ">=1.36.0"


class LibPcapConan(ConanFile):
    name = "libpcap"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/the-tcpdump-group/libpcap"
    description = "libpcap is an API for capturing network traffic"
    license = "BSD-3-Clause"
    topics = ("networking", "pcap", "sniffing", "network-traffic")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_libusb": [True, False],
        "enable_universal": [True, False, "deprecated"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_libusb": False,
        "enable_universal": "deprecated",
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None
    _autotools = None

    # TODO: Add dbus-glib when available
    # TODO: Add libnl-genl when available
    # TODO: Add libbluetooth when available
    # TODO: Add libibverbs when available

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.enable_libusb

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.enable_universal != "deprecated":
            self.output.warn("enable_universal is a deprecated option. Do not use.")

    def requirements(self):
        if self.options.get_safe("enable_libusb"):
            self.requires("libusb/1.0.24")

    def validate(self):
        if tools.scm.Version(self, self.version) < "1.10.0" and self.settings.os == "Macos" and self.options.shared:
            raise ConanInvalidConfiguration("libpcap {} can not be built as shared on OSX.".format(self.version))
        if hasattr(self, "settings_build") and tools.build.cross_building(self, self) and \
           self.options.shared and tools.apple.is_apple_os(self, self.settings.os):
            raise ConanInvalidConfiguration("cross-build of libpcap shared is broken on Apple")
        if tools.scm.Version(self, self.version) < "1.10.1" and self.settings.os == "Windows" and not self.options.shared:
            raise ConanInvalidConfiguration("libpcap can not be built static on Windows below version 1.10.1.")

    def package_id(self):
        del self.info.options.enable_universal

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.build_requires("winflexbison/2.5.24")
        else:
            self.build_requires("bison/3.7.6")
            self.build_requires("flex/2.6.4")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.libs = []
        yes_no = lambda v: "yes" if v else "no"
        configure_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-usb={}".format(yes_no(self.options.get_safe("enable_libusb"))),
            "--disable-universal",
            "--without-libnl",
            "--disable-bluetooth",
            "--disable-packet-ring",
            "--disable-dbus",
            "--disable-rdma",
        ]
        if tools.build.cross_building(self, self):
            target_os = "linux" if self.settings.os == "Linux" else "null"
            configure_args.append("--with-pcap=%s" % target_os)
        elif "arm" in self.settings.arch and self.settings.os == "Linux":
            configure_args.append("--host=arm-linux")
        self._autotools.configure(args=configure_args, configure_dir=self._source_subfolder)
        # Relocatable shared lib on macOS
        tools.files.replace_in_file(self, "Makefile", "-install_name $(libdir)/", "-install_name @rpath/")
        return self._autotools

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if not self.options.shared:
            self._cmake.definitions["ENABLE_REMOTE"] = False
        if self._is_msvc:
            self._cmake.definitions["USE_STATIC_RT"] = "MT" in msvc_runtime_flag(self)
        else:
            # Don't force -static-libgcc for MinGW, because conan users expect
            # to inject this compilation flag themselves
            self._cmake.definitions["USE_STATIC_RT"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        if self.settings.os == "Windows":
            cmake = self._configure_cmake()
            cmake.build()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

        if self.settings.os == "Windows":
            cmake = self._configure_cmake()
            cmake.install()
            tools.files.rm(self, os.path.join(self.package_folder, "bin"), "*.pdb")
            if self.options.shared:
                tools.files.rm(self, os.path.join(self.package_folder, "lib"), "pcap_static.lib")

            def flatten_filetree(folder):
                for file in glob.glob(folder + "/**/*"):
                    shutil.move(file, folder + os.sep)
                for subdir in [dir[0] for dir in os.walk(folder) if dir[0] != folder]:
                    os.rmdir(subdir)

            # libpcap installs into a subfolder like x64 or amd64
            with tools.files.chdir(self, self.package_folder):
                flatten_filetree("bin")
                flatten_filetree("lib")
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
            tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            if self.options.shared:
                tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.a")

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libpcap")
        suffix = "_static" if self.settings.os == "Windows" and not self.options.shared else ""
        self.cpp_info.libs = ["pcap{}".format(suffix)]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
