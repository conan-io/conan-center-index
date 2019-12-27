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
       "stack_walking_unwind": [True, False],
       "stack_walking_backtrace": [True, False],
       "stack_details_auto_detect": [False], # dont let backtrace auto decide
       "stack_details_backtrace_symbol": [True, False],
       "stack_details_dw": [True, False],
       "stack_details_bfd": [True, False],
       "stack_details_dwarf": [True, False],
       "shared": [True, False],
       "fPIC": [True, False]
    }
    default_options = {
       "stack_walking_unwind": True,
       "stack_walking_backtrace": False,
       "stack_details_auto_detect": False,
       "stack_details_dw": False,
       "stack_details_bfd": False,
       "stack_details_dwarf": True,
       "stack_details_backtrace_symbol": False,
       "shared": True,
       "fPIC": True
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"


    def config_options(self):     
          if self.settings.os == "Macos":
            del self.options.stack_details_dw
            del self.options.stack_details_bfd
            del self.options.stack_details_dwarf
    
    def _check_options(self, options):
        sum = 0
        for name, value in self.options.values.as_list():
            if value and name in options:
                sum = sum + 1
        if sum != 1:
            return False
        return True

    def configure(self):
        if self.settings.os not in ["Linux", "Macos", "Android"]:
            raise ConanInvalidConfiguration("upstream backward-cpp v{0} is not \
                supported in {1}.".format(self.version, self.settings.os))
        # windows implementation only available in upstream master branch
        
        if not self._check_options(['stack_walking_unwind', 'stack_walking_backtrace']):
            raise ConanInvalidConfiguration("Please select stack_walking_unwind"
                                            " or stack_walking_backtrace.")

        if self.settings.os in ["Linux", "Android"]:
            if not self._check_options(['stack_details_dw', \
                                        'stack_details_bfd', \
                                        'stack_details_dwarf', \
                                        'stack_details_backtrace_symbol']):
                raise ConanInvalidConfiguration("Please select stack_details_dw"\
                    ", stack_details_bfd, stack_details_dwarf or " \
                    "stack_details_backtrace_symbol.")
    
        if self.settings.os == "Macos":            
            if not self._check_options(['stack_details_backtrace_symbol']):
                raise ConanInvalidConfiguration("Please select stack_details_backtrace_symbol.")

    def requirements(self):
        if self.settings.os in ["Linux", "Android"] and \
           self.options.stack_details_dwarf:
            self.requires("libdwarf/20191104")
    
    def system_requirements(self):
        required_package = None
        if self.settings.os == "Linux":
            if self.options.stack_details_dw:
                required_package = "libdw-dev"
            if self.options.stack_details_bfd:
                required_package = "binutils-dev"
        
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
        cmake.definitions['STACK_WALKING_UNWIND'] = self.options.stack_walking_unwind
        cmake.definitions['STACK_WALKING_BACKTRACE'] = self.options.stack_walking_backtrace
        cmake.definitions['STACK_DETAILS_AUTO_DETECT'] = self.options.stack_details_auto_detect
        cmake.definitions['STACK_DETAILS_BACKTRACE_SYMBOL'] = self.options.stack_details_backtrace_symbol
        cmake.definitions['STACK_DETAILS_DW'] = self.options.stack_details_dw
        cmake.definitions['STACK_DETAILS_BFD'] = self.options.stack_details_bfd
        cmake.definitions['STACK_DETAILS_DWARF'] = self.options.stack_details_dwarf
        cmake.definitions['BACKWARD_SHARED'] = self.options.shared
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="LICENSE*", dst="licenses", src=self._source_subfolder)
        os.remove(os.path.join(self.package_folder, "lib", "backward", "BackwardConfig.cmake"))

    def package_info(self):
        self.cpp_info.names["cmake"] = "Backward"
        self.cpp_info.names["cmake_find_package"] = "Backward"
        self.cpp_info.names["cmake_find_package_multi"] = "Backward"

        self.cpp_info.defines.append('BACKWARD_HAS_UNWIND={}'.format(int(self.options.stack_walking_unwind == True)))
        self.cpp_info.defines.append('BACKWARD_HAS_BACKTRACE={}'.format(int(self.options.stack_walking_backtrace == True)))
        
        self.cpp_info.defines.append('BACKWARD_HAS_BACKTRACE_SYMBOL={}'.format(int(self.options.stack_details_backtrace_symbol == True)))
        self.cpp_info.defines.append('BACKWARD_HAS_DW={}'.format(int(self.options.stack_details_dw == True)))
        self.cpp_info.defines.append('BACKWARD_HAS_BFD={}'.format(int(self.options.stack_details_bfd == True)))
        self.cpp_info.defines.append('BACKWARD_HAS_DWARF={}'.format(int(self.options.stack_details_dwarf == True)))

        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl"])
            if self.options.stack_details_dw:
                self.cpp_info.libs.extend(["dw"])           
            if self.options.stack_details_bfd:
                self.cpp_info.libs.extend(["bfd"])


        
