from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class BackwardCppConan(ConanFile):
    name = "backward-cpp"
    description = "A beautiful stack trace pretty printer for C++"
    homepage = "https://github.com/bombela/backward-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "backward-cpp", "stack-trace")
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "stack_walking" : ["unwind", "backtrace"],
        "stack_details" : ["dw", "bfd", "dwarf", "backtrace_symbol"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "stack_walking": "unwind",
        "stack_details": "dwarf",
    }

    exports_sources = "CMakeLists.txt", "patches/backward-cpp-*.patch"
    generators = "cmake"

    _cmake = None
    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _has_stack_walking(self, type):
        return self.options.stack_walking == type

    def _has_stack_details(self, type):
        return False if self.settings.os == "Windows" else self.options.stack_details == type

    def _supported_os(self):
        return ["Linux", "Macos", "Android", "Windows"] if tools.Version(self.version) >= "1.5" \
               else ["Linux", "Macos", "Android"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.stack_details

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.settings.os in ["Linux", "Android"] and \
           self._has_stack_details("dwarf"):
            self.requires("libdwarf/20191104")

    def system_requirements(self):
        required_package = None
        if self.settings.os == "Linux":
            if self._has_stack_details("dw"):
                if tools.os_info.linux_distro in ["ubuntu", "debian"]:
                    required_package = "libdw-dev"
                elif tools.os_info.linux_distro in ["fedora", "centos"]:
                    required_package = "elfutils-libs"
                elif tools.os_info.linux_distro == "opensuse":
                    required_package = "libdw-devel"
                elif tools.os_info.linux_distro == "arch":
                    required_package = "libelf"

            if self._has_stack_details("bfd"):
                if tools.os_info.linux_distro in ["ubuntu", "debian"]:
                    required_package = "binutils-dev"
                elif tools.os_info.linux_distro in ["fedora", "centos", "opensuse"]:
                    required_package = "binutils-devel"
                elif tools.os_info.linux_distro == "arch":
                    required_package = "binutils"
                elif tools.os_info.is_freebsd:
                    required_package = "libbfd"

        if required_package != None:
            installer = tools.SystemPackageTool()
            if not installer.installed(required_package):
                raise ConanInvalidConfiguration("backward-cpp requires {}.".format(required_package))

    def validate(self):
        if self.settings.os not in self._supported_os():
            raise ConanInvalidConfiguration("upstream backward-cpp v{0} is not"
                " supported in {1}.".format(self.version, self.settings.os))
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 17)
        if (self.settings.compiler == "gcc" or self.settings.compiler == "clang") and tools.Version(self.settings.compiler.version) <= 5:
            raise ConanInvalidConfiguration("Compiler version is not supported")
        if self.settings.os == "Macos" and \
                not self._has_stack_details("backtrace_symbol"):
            raise ConanInvalidConfiguration("only stack_details=backtrace_symbol"
                                            " is supported on Macos")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["STACK_WALKING_UNWIND"] = self._has_stack_walking("unwind")
        self._cmake.definitions["STACK_WALKING_BACKTRACE"] = self._has_stack_walking("backtrace")
        self._cmake.definitions["STACK_DETAILS_AUTO_DETECT"] = False
        self._cmake.definitions["STACK_DETAILS_BACKTRACE_SYMBOL"] = self._has_stack_details("backtrace_symbol")
        self._cmake.definitions["STACK_DETAILS_DW"] = self._has_stack_details("dw")
        self._cmake.definitions["STACK_DETAILS_BFD"] = self._has_stack_details("bfd")
        self._cmake.definitions["STACK_DETAILS_DWARF"] = self._has_stack_details("dwarf")
        self._cmake.definitions["BACKWARD_SHARED"] = self.options.shared
        self._cmake.definitions["BACKWARD_TESTS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        os.remove(os.path.join(self.package_folder, "lib", "backward", "BackwardConfig.cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Backward"
        self.cpp_info.names["cmake_find_package_multi"] = "Backward"

        self.cpp_info.defines.append("BACKWARD_HAS_UNWIND={}".format(int(self._has_stack_walking("unwind"))))
        self.cpp_info.defines.append("BACKWARD_HAS_BACKTRACE={}".format(int(self._has_stack_walking("backtrace"))))

        self.cpp_info.defines.append("BACKWARD_HAS_BACKTRACE_SYMBOL={}".format(int(self._has_stack_details("backtrace_symbol"))))
        self.cpp_info.defines.append("BACKWARD_HAS_DW={}".format(int(self._has_stack_details("dw"))))
        self.cpp_info.defines.append("BACKWARD_HAS_BFD={}".format(int(self._has_stack_details("bfd"))))
        self.cpp_info.defines.append("BACKWARD_HAS_DWARF={}".format(int(self._has_stack_details("dwarf"))))
        self.cpp_info.defines.append("BACKWARD_HAS_PDB_SYMBOL={}".format(int(self.settings.os == "Windows")))

        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl"])
            if self._has_stack_details("dw"):
                self.cpp_info.system_libs.extend(["dw"])
            if self._has_stack_details("bfd"):
                self.cpp_info.system_libs.extend(["bfd"])
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["psapi", "dbghelp"])
