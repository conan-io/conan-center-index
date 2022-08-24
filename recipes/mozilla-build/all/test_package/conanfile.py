from conan import ConanFile, tools$
import os


class TestPackageConan(ConanFile):

    def test(self):
        tools.files.save(self, "file.txt", "some text")
        assert not os.path.isdir("destionation")
        self.run("nsinstall -D destination")
        assert os.path.isdir("destination")
        assert not os.path.isfile(os.path.join("destination", "file.txt"))
        self.run("nsinstall -t -m 644 file.txt destination")
        assert os.path.isfile(os.path.join("destination", "file.txt"))

