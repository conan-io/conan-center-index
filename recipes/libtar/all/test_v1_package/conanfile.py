from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import os
import tarfile


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        with tarfile.open("test.tar", "w", format=tarfile.GNU_FORMAT) as f:
            import io
            bio = io.BytesIO()
            bio.write(b"secret text\n")
            tarinfo = tarfile.TarInfo("hello_world")
            tarinfo.size = bio.tell()
            import time
            tarinfo.mtime = time.time()
            bio.seek(0)
            f.addfile(tarinfo, bio)

        if not tools.cross_building(self):
            if os.path.exists("hello_world"):
                raise ConanException("file extracted by tar archive should not exist yet")
            bin_path = os.path.join("bin", "test_package")
            self.run(f"{bin_path} test.tar", run_environment=True)
            if not os.path.exists("hello_world"):
                raise ConanException("file not extracted")
            extracted_text = tools.load("hello_world")
            if extracted_text != "secret text\n":
                raise ConanException(f"File not loaded correctly. Got \"{repr(extracted_text)}\"")

            self.run("libtar -t test.tar", run_environment=True)
