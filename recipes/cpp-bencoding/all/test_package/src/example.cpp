#include <bencoding/bencoding.h>

#include <iostream>
#include <string>

int main() {
	using namespace std::string_literals;
	std::cout << bencoding::getPrettyRepr(bencoding::decode("d8:announce18:http://tracker.com10:created by14:KTorrent 2.1.413:creation datei1182163277e4:infod6:lengthi6e4:name8:file.txt12:piece lengthi32768e6:pieces20:the-binary-data-of20ee"s));
}
