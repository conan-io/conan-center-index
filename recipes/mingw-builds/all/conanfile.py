import os
from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration


class MingwConan(ConanFile):
    name = "mingw-builds"
    description = "MinGW is a contraction of Minimalist GNU for Windows"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ericLemanissier/mingw-builds"
    license = "ZPL-2.1", "MIT", "GPL-2.0-or-later"
    topics = ("gcc", "gnu", "unix", "mingw32", "binutils")
    settings = "os", "arch"
    options = {"threads": ["posix", "win32"], "exception": ["seh", "sjlj"]}
    default_options = {"threads": "posix", "exception": "seh"}
    
    provides = "mingw-w64"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def validate(self):
        valid_os = ["Windows"]
        if str(self.settings.os) not in valid_os:
            raise ConanInvalidConfiguration("MinGW {} is only supported for the following operating systems: {}"
                                            .format(self.version, valid_os))
        valid_arch = ["x86_64"]
        if str(self.settings.arch) not in valid_arch:
            raise ConanInvalidConfiguration("MinGW {} is only supported for the following architectures on {}: {}"
                                            .format(self.version, str(self.settings.os), valid_arch))
            
        if getattr(self, "settings_target", None):
            if str(self.settings_target.os) not in valid_os:
                raise ConanInvalidConfiguration("MinGW {} is only supported for the following operating systems: {}"
                                                .format(self.version, valid_os))
            valid_arch = ["x86_64"]
            if str(self.settings_target.arch) not in valid_arch:
                raise ConanInvalidConfiguration("MinGW {} is only supported for the following architectures on {}: {}"
                                                .format(self.version, str(self.settings.os), valid_arch))
            if self.settings_target.compiler != "gcc":
                raise ConanInvalidConfiguration("Only GCC is allowed as compiler.")
            if str(self.settings_target.compiler.threads) != str(self.options.threads):
                raise ConanInvalidConfiguration("Build requires 'mingw' provides binaries for gcc "
                                                "with threads={}, your profile:host declares "
                                                "threads={}, please use the same value for both."
                                                .format(self.options.threads,
                                                        self.settings_target.compiler.threads))
            if str(self.settings_target.compiler.exception) != str(self.options.exception):
                raise ConanInvalidConfiguration("Build requires 'mingw' provides binaries for gcc "
                                                "with exception={}, your profile:host declares "
                                                "exception={}, please use the same value for both."
                                                .format(self.options.exception,
                                                        self.settings_target.compiler.exception))

    def build_requirements(self):
        self.build_requires("7zip/19.00")

    def build(self):
        # Source should be downloaded in the build step since it depends on specific options
        url = self.conan_data["sources"][self.version][str(self.options.threads)][str(self.options.exception)]
        self.output.info("Downloading: %s" % url["url"])
        tools.download(url["url"], "file.7z", sha256=url["sha256"])
        self.run("7z x file.7z")
        os.remove('file.7z')


    def package(self):
        target = "mingw64" if self.settings.arch == "x86_64" else "mingw32"
        self.copy("*", dst="", src=target)
        tools.rmdir(target)
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "opt", "lib", "cmake"))

    def package_info(self):
        if getattr(self, "settings_target", None):
            if self.settings_target.compiler != "gcc":
                raise ConanInvalidConfiguration("Only GCC is allowed as compiler.")
            if str(self.settings_target.compiler.threads) != str(self.options.threads):
                raise ConanInvalidConfiguration("Build requires 'mingw' provides binaries for gcc "
                                                "with threads={}, your profile:host declares "
                                                "threads={}, please use the same value for both."
                                                .format(self.options.threads,
                                                        self.settings_target.compiler.threads))
            if str(self.settings_target.compiler.exception) != str(self.options.exception):
                raise ConanInvalidConfiguration("Build requires 'mingw' provides binaries for gcc "
                                                "with exception={}, your profile:host declares "
                                                "exception={}, please use the same value for both."
                                                .format(self.options.exception,
                                                        self.settings_target.compiler.exception))

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
        self.env_info.MINGW_HOME = str(self.package_folder)

        self.env_info.CONAN_CMAKE_GENERATOR = "MinGW Makefiles"
        self.env_info.CXX = os.path.join(self.package_folder, "bin", "g++.exe").replace("\\", "/")
        self.env_info.CC = os.path.join(self.package_folder, "bin", "gcc.exe").replace("\\", "/")
        self.env_info.LD = os.path.join(self.package_folder, "bin", "ld.exe").replace("\\", "/")
        self.env_info.NM = os.path.join(self.package_folder, "bin", "nm.exe").replace("\\", "/")
        self.env_info.AR = os.path.join(self.package_folder, "bin", "ar.exe").replace("\\", "/")
        self.env_info.AS = os.path.join(self.package_folder, "bin", "as.exe").replace("\\", "/")
        self.env_info.STRIP = os.path.join(self.package_folder, "bin", "strip.exe").replace("\\", "/")
        self.env_info.RANLIB = os.path.join(self.package_folder, "bin", "ranlib.exe").replace("\\", "/")
        self.env_info.STRINGS = os.path.join(self.package_folder, "bin", "strings.exe").replace("\\", "/")
        self.env_info.OBJDUMP = os.path.join(self.package_folder, "bin", "objdump.exe").replace("\\", "/")
        self.env_info.GCOV = os.path.join(self.package_folder, "bin", "gcov.exe").replace("\\", "/")
