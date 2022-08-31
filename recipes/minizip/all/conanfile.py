from conan import ConanFile
from conan.tools import files
from conans import CMake
import functools

required_conan_version = ">=1.46.0"


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

    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("zlib/1.2.12")
        if self.options.bzip2:
            self.requires("bzip2/1.0.8")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_BZIP2"] = self.options.bzip2
        cmake.definitions["BUILD_TOOLS"] = self.options.tools
        cmake.configure()
        return cmake

    def build(self):
        files.apply_conandata_patches(self)
        cmake = self._configure_cmake()
        cmake.build()

    def _extract_license(self):
        with files.chdir(self, f"{self.source_folder}/{self._source_subfolder}"):
            tmp = files.load(self, "zlib.h")
            license_contents = tmp[2:tmp.find("*/", 1)]
            files.save(self, "LICENSE", license_contents)

    def package(self):
        self._extract_license()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["minizip"]
        self.cpp_info.includedirs = ["include", "include/minizip"]
        if self.options.bzip2:
            self.cpp_info.defines.append("HAVE_BZIP2")

        if self.options.tools:
            bin_path = f"{self.package_folder}/bin"
            self.output.info(f"Appending PATH environment variable: {bin_path}")
            self.env_info.PATH.append(bin_path)
