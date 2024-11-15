// Define for suppress warning STL4015 : The std::iterator class template (used as a base class to provide typedefs) is deprecated in C++17.
// ToDo: Remove when new version of RapidJson will be available
#define _SILENCE_CXX17_ITERATOR_BASE_CLASS_DEPRECATION_WARNING

#include <bitserializer/bit_serializer.h>
#ifdef WITH_CPPRESTSDK
#include <bitserializer/cpprestjson_archive.h>
#endif
#ifdef WITH_RAPIDJSON
#include <bitserializer/rapidjson_archive.h>
#endif
#ifdef WITH_PUGIXML
#include <bitserializer/pugixml_archive.h>
#endif
#ifdef WITH_RAPIDYAML
#include <bitserializer/rapidyaml_archive.h>
#endif
#ifdef WITH_CSV
#include <bitserializer/csv_archive.h>
#endif
#ifdef WITH_MSGPACK
#include <bitserializer/msgpack_archive.h>
#endif

#include <iostream>
#include <sstream>
#include <filesystem>

class CTest
{
public:
	CTest(std::string message)
		: mMessage(std::move(message))
	{ }

	template <class TArchive>
	void Serialize(TArchive& archive)
	{
#if BITSERIALIZER_VERSION >= 7000
		archive << BitSerializer::KeyValue("Message", mMessage);
#else
		archive << BitSerializer::MakeAutoKeyValue("Message", mMessage);
#endif
	}

	std::string mMessage;
};

std::string PrintAsHexString(const std::string& data)
{
	constexpr char hexChars[] = "0123456789ABCDEF";
	std::string result;
	for (const char ch : data)
	{
		if (!result.empty()) result.push_back(' ');
		result.append({ hexChars[(ch & 0xF0) >> 4], hexChars[(ch & 0x0F) >> 0] });
	}
	return result;
}

template <typename TArchive>
void TestArchive(const std::string& message)
{
	std::cout << "Testing " << BitSerializer::Convert::ToString(TArchive::archive_type) << " archive: ";

	BitSerializer::SerializationOptions serializationOptions;
	serializationOptions.streamOptions.writeBom = false;

	CTest testObj[1] = { message };
	std::stringstream outputStream;
	BitSerializer::SaveObject<TArchive>(testObj, outputStream, serializationOptions);
#if BITSERIALIZER_VERSION >= 7000
	const std::string result = TArchive::is_binary ? PrintAsHexString(outputStream.str()) : outputStream.str();
#else
	const std::string result = outputStream.str();
#endif
	std::cout << result<< std::endl;
}

int main() {
	std::cout << "BitSerializer version: "
#ifdef BITSERIALIZER_VERSION
		<< BitSerializer::Convert::To<std::string>(BITSERIALIZER_VERSION_MAJOR) << "."
		<< BitSerializer::Convert::To<std::string>(BITSERIALIZER_VERSION_MINOR) << "."
		<< BitSerializer::Convert::To<std::string>(BITSERIALIZER_VERSION_PATCH)
#else
		<< BitSerializer::Convert::To<std::string>(BitSerializer::Version::Major) << "."
		<< BitSerializer::Convert::To<std::string>(BitSerializer::Version::Minor) << "."
		<< BitSerializer::Convert::To<std::string>(BitSerializer::Version::Maintenance)
#endif
		<< std::endl;

#if !defined BITSERIALIZER_VERSION || BITSERIALIZER_HAS_FILESYSTEM
	// Some compilers does not link filesystem automatically
	std::cout << "Testing the link of C++17 filesystem: " << std::filesystem::temp_directory_path() << std::endl;
#endif

#ifdef WITH_CPPRESTSDK
	TestArchive<BitSerializer::Json::CppRest::JsonArchive>("Implementation based on cpprestsdk");
#endif
#ifdef WITH_RAPIDJSON
	TestArchive<BitSerializer::Json::RapidJson::JsonArchive>("Implementation based on RapidJson");
#endif
#ifdef WITH_PUGIXML
	TestArchive<BitSerializer::Xml::PugiXml::XmlArchive>("Implementation based on pugixml");
#endif
#ifdef WITH_RAPIDYAML
    TestArchive<BitSerializer::Yaml::RapidYaml::YamlArchive>("Implementation based on RapidYaml");
#endif
#ifdef WITH_CSV
	TestArchive<BitSerializer::Csv::CsvArchive>("CSV archive (built-in implementation)");
#endif
#ifdef WITH_MSGPACK
	TestArchive<BitSerializer::MsgPack::MsgPackArchive>("MsgPack archive (built-in implementation)");
#endif
}
