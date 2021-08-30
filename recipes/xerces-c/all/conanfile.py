from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class XercesCConan(ConanFile):
    name = "xerces-c"
    description = (
        "Xerces-C++ is a validating XML parser written in a portable subset of C++"
    )
    topics = ("conan", "xerces", "XML", "validation", "DOM", "SAX", "SAX2")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://xerces.apache.org/xerces-c/index.html"
    license = "Apache-2.0"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        # https://xerces.apache.org/xerces-c/build-3.html
        "char_type": ["uint16_t", "char16_t", "wchar_t"],
        "network_accessor": ["curl", "socket", "cfurl", "winsock"],
        "transcoder": ["gnuiconv", "iconv", "icu", "macosunicodeconverter", "windows"],
        "message_loader": ["inmemory", "icu", "iconv"],
        "mutex_manager": ["standard", "posix", "windows"],
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _validate(self, option, value, os):
        """
        Validate that the given `option` has the required `value` for the given `os`
        If not raises a ConanInvalidConfiguration error

        :param option: the name of the option to validate
        :param value: the value that the `option` should have
        :param os: either a single string or a tuple of strings containing the
                   OS(es) that `value` is valid on
        """
        if ((isinstance(os, str) and self.settings.os != os) or \
            (isinstance(os, tuple) and self.settings.os not in os)) \
             and getattr(self.options, option) == value:
            raise ConanInvalidConfiguration(
                "Option '{option}={value}' is only supported on {os}".format(
                    option=option, value=value, os=os
                )
            )

    def validate(self):
        self._validate("char_type", "wchar_t", "Windows")
        self._validate("network_accessor", "winsock", "Windows")
        self._validate("network_accessor", "cfurl", "Macos")
        self._validate("network_accessor", "socket", ("Linux", "Macos"))
        self._validate("network_accessor", "curl", ("Linux", "Macos"))
        self._validate("transcoder", "macosunicodeconverter", "Macos")
        self._validate("transcoder", "windows", "Windows")
        self._validate("mutex_manager", "posix", ("Linux", "Macos"))
        self._validate("mutex_manager", "windows", "Windows")

    def requirements(self):
        if "icu" in (self.options.transcoder, self.options.message_loader):
            self.requires("icu/69.1")

    def config_options(self):
        self.options.shared = False
        self.options.fPIC = True
        self.options.char_type = "uint16_t"
        self.options.message_loader = "inmemory"

        if self.settings.os == "Windows":
            del self.options.fPIC
            self.options.network_accessor = "winsock"
            self.options.transcoder = "windows"
            self.options.mutex_manager = "windows"
        elif self.settings.os == "Macos":
            self.options.network_accessor = "cfurl"
            self.options.transcoder = "macosunicodeconverter"
            self.options.mutex_manager = "posix"
        elif self.settings.os == "Linux":
            self.options.network_accessor = "socket"
            self.options.transcoder = "gnuiconv"
            self.options.mutex_manager = "posix"

    def configure(self):
        if self.settings.os not in ("Windows", "Macos", "Linux"):
            raise ConanInvalidConfiguration("OS is not supported")
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        # https://xerces.apache.org/xerces-c/build-3.html
        self._cmake.definitions["network-accessor"] = self.options.network_accessor
        self._cmake.definitions["transcoder"] = self.options.transcoder
        self._cmake.definitions["message-loader"] = "inmemory"
        self._cmake.definitions["xmlch-type"] = self.options.char_type
        self._cmake.definitions["mutex-manager"] = self.options.mutex_manager
        # avoid picking up system dependency
        self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_CURL"] = self.options.network_accessor != "curl"
        self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_ICU"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # remove unneeded directories
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreFoundation", "CoreServices"]
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        if self.options.network_accessor == "curl":
            self.cpp_info.system_libs.append("curl")
        self.cpp_info.names["cmake_find_package"] = "XercesC"
        self.cpp_info.names["cmake_find_package_multi"] = "XercesC"
