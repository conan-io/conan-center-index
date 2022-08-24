from conan import ConanFile, tools
from conans import CMake
import os


class CgltfConan(ConanFile):
    name = "cgltf"
    description = "Single-file glTF 2.0 loader and writer written in C99."
    license = "MIT"
    topics = ("conan", "cgltf", "gltf", "header-only")
    homepage = "https://github.com/jkuhlmann/cgltf"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    exports_sources = "CMakeLists.txt"
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

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _create_source_files(self):
        cgltf_c = (
            "#define CGLTF_IMPLEMENTATION\n"
            "#include \"cgltf.h\"\n"
        )
        cgltf_write_c = (
            "#define CGLTF_WRITE_IMPLEMENTATION\n"
            "#include \"cgltf_write.h\"\n"
        )
        tools.save(os.path.join(self.build_folder, self._source_subfolder, "cgltf.c"), cgltf_c)
        tools.save(os.path.join(self.build_folder, self._source_subfolder, "cgltf_write.c"), cgltf_write_c)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._create_source_files()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        for header_file in ["cgltf.h", "cgltf_write.h"]:
            header_fullpath = os.path.join(self.package_folder, "include", header_file)
            self._remove_implementation(header_fullpath)

    @staticmethod
    def _remove_implementation(header_fullpath):
        header_content = tools.files.load(self, header_fullpath)
        begin = header_content.find("/*\n *\n * Stop now, if you are only interested in the API.")
        end = header_content.find("/* cgltf is distributed under MIT license:", begin)
        implementation = header_content[begin:end]
        tools.replace_in_file(
            header_fullpath,
            implementation,
            (
                "/**\n"
                " * Implementation removed by conan during packaging.\n"
                " * Don't forget to link libs provided in this package.\n"
                " */\n\n"
            )
        )

    def package_info(self):
        self.cpp_info.libs = ["cgltf"]
