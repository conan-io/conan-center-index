import os
import glob
from conans import ConanFile, CMake, tools


class MikkTSpaceConan(ConanFile):
    name = "mikktspace"
    description = " A common standard for tangent space used in baking tools to produce normal maps."
    homepage = "https://github.com/mmikk/MikkTSpace"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Zlib"
    topics = ("conan", "tangent", "space", "normal")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False
    }

    generators = "cmake"
    exports_sources = ['CMakeLists.txt']

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob('MikkTSpace-*/')[0]
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    @property
    def _extracted_license(self):
        content_lines = open(os.path.join(self.source_folder, self._source_subfolder, "mikktspace.h")).readlines()
        license_content = []
        for i in range(4, 21):
            license_content.append(content_lines[i][4:-1])
        return "\n".join(license_content)

    def package(self):
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), self._extracted_license)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["mikktspace"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
