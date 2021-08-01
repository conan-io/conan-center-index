from conans import ConanFile, tools, CMake
import os

required_conan_version = ">=1.33.0"


class MinizipConan(ConanFile):
    name = "minizip"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://zlib.net"
    license = "Zlib"
    description = "An experimental package to read and write files in .zip format, written on top of zlib"
    topics = ("zip", "compression", "inflate")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "bzip2": [True, False],
        "tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "bzip2": True,
        "tools": False,
    }

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("zlib/1.2.11")
        if self.options.bzip2:
            self.requires("bzip2/1.0.8")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_BZIP2"] = self.options.bzip2
        self._cmake.definitions["BUILD_TOOLS"] = self.options.tools
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _extract_license(self):
        tmp = tools.load(os.path.join(self._source_subfolder, "zlib.h"))
        return tmp[2:tmp.find("*/", 1)]

    def package(self):
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"),
                   self._extract_license())
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["minizip"]
        self.cpp_info.includedirs = ["include", os.path.join("include", "minizip")]
        if self.options.bzip2:
            self.cpp_info.defines.append("HAVE_BZIP2")

        if self.options.tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
