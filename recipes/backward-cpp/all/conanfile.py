from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class BackwardCppConan(ConanFile):
    name = "backward-cpp"
    description = "A beautiful stack trace pretty printer for C++"
    homepage = "https://github.com/bombela/backward-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "backward-cpp", "stack-trace")
    license = "MIT"
    exports_sources = [ "CMakeLists.txt", "patches/backward-cpp-*.patch" ]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {
       "stack_walking" : ["unwind", "backtrace"],
       "stack_details" : ["dw", "bfd", "dwarf", "backtrace_symbol"],
       "shared": [True, False],
       "fPIC": [True, False]
    }
    default_options = {
       "stack_walking": "unwind",
       "stack_details": "dwarf",
       "shared": True,
       "fPIC": True
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

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
        if self.settings.os not in self._supported_os():
            raise ConanInvalidConfiguration("upstream backward-cpp v{0} is not \
                supported in {1}.".format(self.version, self.settings.os))

        if self.settings.os == "Macos" and \
           not self._has_stack_details("backtrace_symbol"):
            raise ConanInvalidConfiguration("only stack_details=backtrace_symbol"
                                            " is supported on Macos")
        
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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['STACK_WALKING_UNWIND'] = self._has_stack_walking("unwind")
        cmake.definitions['STACK_WALKING_BACKTRACE'] = self._has_stack_walking("backtrace")
        cmake.definitions['STACK_DETAILS_AUTO_DETECT'] = False
        cmake.definitions['STACK_DETAILS_BACKTRACE_SYMBOL'] = self._has_stack_details("backtrace_symbol")
        cmake.definitions['STACK_DETAILS_DW'] = self._has_stack_details("dw")
        cmake.definitions['STACK_DETAILS_BFD'] = self._has_stack_details("bfd")
        cmake.definitions['STACK_DETAILS_DWARF'] = self._has_stack_details("dwarf")
        cmake.definitions['BACKWARD_SHARED'] = self.options.shared
        cmake.definitions['BACKWARD_TESTS'] = False
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def _patch_sources(self):
        if "patches" in self.conan_data:
            if self.version in self.conan_data["patches"]:
                for patch in self.conan_data["patches"][self.version]:
                    tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="LICENSE*", dst="licenses", src=self._source_subfolder)
        os.remove(os.path.join(self.package_folder, "lib", "backward", "BackwardConfig.cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Backward"
        self.cpp_info.names["cmake_find_package_multi"] = "Backward"

        self.cpp_info.defines.append('BACKWARD_HAS_UNWIND={}'.format(int(self._has_stack_walking("unwind"))))
        self.cpp_info.defines.append('BACKWARD_HAS_BACKTRACE={}'.format(int(self._has_stack_walking("backtrace"))))
        
        self.cpp_info.defines.append('BACKWARD_HAS_BACKTRACE_SYMBOL={}'.format(int(self._has_stack_details("backtrace_symbol"))))
        self.cpp_info.defines.append('BACKWARD_HAS_DW={}'.format(int(self._has_stack_details("dw"))))
        self.cpp_info.defines.append('BACKWARD_HAS_BFD={}'.format(int(self._has_stack_details("bfd"))))
        self.cpp_info.defines.append('BACKWARD_HAS_DWARF={}'.format(int(self._has_stack_details("dwarf"))))
        self.cpp_info.defines.append('BACKWARD_HAS_PDB_SYMBOL={}'.format(int(self.settings.os == "Windows")))

        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl"])
            if self._has_stack_details("dw"):
                self.cpp_info.system_libs.extend(["dw"])           
            if self._has_stack_details("bfd"):
                self.cpp_info.system_libs.extend(["bfd"])
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["psapi", "dbghelp"])


        
