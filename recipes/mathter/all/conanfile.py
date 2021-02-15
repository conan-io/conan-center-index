from conans import ConanFile, tools
import os

class MathterConan(ConanFile):
    name = "mathter"
    license = "MIT"
    homepage = "https://github.com/petiaccja/Mathter"
    url = "https://github.com/conan-io/conan-center-index/"
    description = "Powerful 3D math and small-matrix linear algebra library for games and science."
    topics = ("game-dev", "linear-algebra", "vector-math", "matrix-library")
    exports_sources = "Mathter/*"
    no_copy_source = True
    settings = { "cppstd": ["17", "20"] }
        
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("Mathter-" + self.version, "sources")
            
    def package(self):
        self.copy("*.hpp", dst="include/Mathter", src="sources/Mathter")
        self.copy("*.natvis", dst="include/Mathter", src="sources/Mathter")
        self.copy("LICENCE", dst="licenses", src="sources")

    def package_id(self):
        self.info.header_only()
