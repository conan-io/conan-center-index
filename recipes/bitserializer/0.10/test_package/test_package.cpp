// Define for suppress warning STL4015 : The std::iterator class template (used as a base class to provide typedefs) is deprecated in C++17.
// ToDo: Remove when new version of RapidJson will be available
#define _SILENCE_CXX17_ITERATOR_BASE_CLASS_DEPRECATION_WARNING

#include <iostream>
#include <sstream>
#include <filesystem>
#include "bitserializer/bit_serializer.h"
#include "bitserializer/rapidjson_archive.h"

class CTest
{
public:
	CTest(std::string message)
		: mMessage(std::move(message))
	{ }

	template <class TArchive>
	void Serialize(TArchive& archive)
	{
		archive << BitSerializer::MakeAutoKeyValue("Message", mMessage);
	}

	std::string mMessage;
};

template <typename TArchive>
void TestArchive(const std::string& message)
{
	std::cout << "Testing " << BitSerializer::Convert::ToString(TArchive::archive_type) << " archive: ";

	BitSerializer::SerializationOptions serializationOptions;
	serializationOptions.streamOptions.writeBom = false;

	CTest testObj(message);
	std::stringstream outputStream;
	BitSerializer::SaveObject<TArchive>(testObj, outputStream, serializationOptions);
	std::cout << outputStream.str() << std::endl;
}

int main() {
	std::cout << "BitSerializer version: "
		<< BitSerializer::Convert::To<std::string>(BitSerializer::Version::Major) << "."
		<< BitSerializer::Convert::To<std::string>(BitSerializer::Version::Minor) << "."
		<< BitSerializer::Convert::To<std::string>(BitSerializer::Version::Maintenance)
		<< std::endl;

	// Some compilers does not link filesystem automatically
	std::cout << "Testing the link of C++17 filesystem: " << std::filesystem::temp_directory_path() << std::endl;

	TestArchive<BitSerializer::Json::RapidJson::JsonArchive>("Implementation based on RapidJson");
}
