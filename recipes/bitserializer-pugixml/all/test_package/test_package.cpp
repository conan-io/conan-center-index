#include <iostream>
#include <sstream>
#include "bitserializer/bit_serializer.h"
#include "bitserializer_pugixml/pugixml_archive.h"

using namespace BitSerializer;
using XmlArchive = BitSerializer::Xml::PugiXml::XmlArchive;

class CTest
{
public:
	CTest(std::string message)
		: mMessage(std::move(message))
	{ }

	template <class TArchive>
	void Serialize(TArchive& archive)
	{
		archive << MakeAutoAttributeValue("Message", mMessage);
	}

	std::string mMessage;
};

int main() {
	BitSerializer::SerializationOptions serializationOptions;
	serializationOptions.streamOptions.writeBom = false;

	CTest testObj("BitSerializer XML archive");

	std::stringstream outputStream;
	BitSerializer::SaveObject<XmlArchive>(testObj, outputStream, serializationOptions);
	std::cout << outputStream.str() << std::endl;

	return 0;
}
