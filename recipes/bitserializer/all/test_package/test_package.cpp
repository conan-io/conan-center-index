// Define for suppress warning STL4015 : The std::iterator class template (used as a base class to provide typedefs) is deprecated in C++17.
// ToDo: Remove when new version of RapidJson will be available
#define _SILENCE_CXX17_ITERATOR_BASE_CLASS_DEPRECATION_WARNING

#include <iostream>
#include <sstream>
#include <filesystem>
#include "bitserializer/bit_serializer.h"
#include "bitserializer_rapidjson/rapidjson_archive.h"
// ToDo: Will need to check that components are available (via #ifdef)
// #include "bitserializer_cpprest_json/cpprest_json_archive.h"
// #include "bitserializer_pugixml/pugixml_archive.h"
// #include "bitserializer_rapidyaml/rapidyaml_archive.h"

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
void TestArchive(const std::string& archiveType, const std::string& message)
{
	std::cout << "Testing " << archiveType << " archive: ";

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

	TestArchive<BitSerializer::Json::RapidJson::JsonArchive>("JSON", "Implementation based on RapidJson");

	// ToDo: Uncomment when Conan will support components (will need to check that component is available, like via #ifdef)
	// TestArchive<BitSerializer::Json::CppRest::JsonArchive>("JSON", "Implementation based on CppRestSdk");

	// ToDo: Uncomment when Conan will support components and PugiXml will be available in the Conan-center
	// TestArchive<BitSerializer::Xml::PugiXml::XmlArchive>("XML", "Implementation based on PugiXml");

	// ToDo: Uncomment when Conan will support components and RapidYaml will be available in the Conan-center
	// TestArchive<BitSerializer::Yaml::RapidYaml::YamlArchive>("YAML", "Implementation based on RapidYaml");
}
