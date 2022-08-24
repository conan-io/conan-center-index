from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class BackwardCppConan(ConanFile):
    name = "backward-cpp"
    description = "A beautiful stack trace pretty printer for C++"
    homepage = "https://github.com/bombela/backward-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("backward-cpp", "stack-trace")
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

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _supported_os(self):
        supported_os = ["Linux", "Macos", "Android"]
        if tools.Version(self.version) >= "1.5":
            supported_os.append("Windows")
        return supported_os

    def _has_stack_walking(self, type):
        return self.options.stack_walking == type

    def _has_stack_details(self, type):
        return False if self.settings.os == "Windows" else self.options.stack_details == type

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.stack_details
        # default option
        if self.settings.os == "Macos":
            self.options.stack_details = "backtrace_symbol"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.settings.os in ["Linux", "Android"]:
            if self._has_stack_details("dwarf"):
                self.requires("libdwarf/20191104")
            if self._has_stack_details("dw"):
                self.requires("elfutils/0.186")
            if self._has_stack_details("bfd"):
                self.requires("binutils/2.38")

    def validate(self):
        if self.settings.os not in self._supported_os:
            raise ConanInvalidConfiguration("upstream backward-cpp v{0} is not"
                " supported in {1}.".format(self.version, self.settings.os))
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        if self.settings.os == "Macos":
            if self.settings.arch == "armv8":
                raise ConanInvalidConfiguration("Macos M1 not supported yet")
            if not self._has_stack_details("backtrace_symbol"):
                raise ConanInvalidConfiguration("only stack_details=backtrace_symbol"
                                                " is supported on Macos")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
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
            tools.files.patch(self, **patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "backward"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Backward")
        self.cpp_info.set_property("cmake_target_name", "Backward::Backward")

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
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["psapi", "dbghelp"])

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Backward"
        self.cpp_info.names["cmake_find_package_multi"] = "Backward"
