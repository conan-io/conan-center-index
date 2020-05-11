#include <iostream>
#include <sstream>
#include "bitserializer/bit_serializer.h"
#include "bitserializer_cpprest_json/cpprest_json_archive.h"

using namespace BitSerializer;
using JsonArchive = BitSerializer::Json::CppRest::JsonArchive;

int main() {
	BitSerializer::SerializationOptions serializationOptions;
	serializationOptions.streamOptions.writeBom = false;

	std::string testObj = "BitSerializer JSON archive (based on CppRestJson)";

	std::stringstream outputStream;
	BitSerializer::SaveObject<JsonArchive>(testObj, outputStream, serializationOptions);
	std::cout << outputStream.str() << std::endl;

	return 0;
}
