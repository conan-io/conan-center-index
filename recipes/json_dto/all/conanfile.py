from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

class JsondtoConan(ConanFile):
    name = "json_dto"
    license = "BSD-3-Clause"
    homepage = "https://github.com/Stiffstream/json_dto"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A small header-only helper for converting data between json representation and c++ structs"
    topics = ("json", "dto", "serialization")
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("rapidjson/1.1.0")

    def configure(self):
        minimal_cpp_standard = "14"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)
        minimal_version = {
            "gcc": "5",
            "clang": "4",
            "apple-clang": "8",
            "Visual Studio": "15"
        }
        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                "%s recipe lacks information about the %s compiler standard version support" % (self.name, compiler))
            self.output.warn(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))
            return

        version = tools.Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))


    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["JSON_DTO_INSTALL"] = True
        self._cmake.definitions["JSON_DTO_FIND_DEPS"] = False
        self._cmake.configure(source_folder=os.path.join(self._source_subfolder, "dev", "json_dto"))
        return self._cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-v." + self.version
        os.rename(extracted_dir, self._source_subfolder )

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_id(self):
        self.info.header_only()
