#include <cstdlib>
#include <iostream>

#include <google/protobuf/timestamp.pb.h>
#include <google/protobuf/util/time_util.h>

#include <google/protobuf/compiler/versions.h>

int main()
{
	google::protobuf::Timestamp ts;
	google::protobuf::util::TimeUtil::FromString("1972-01-01T10:00:20.021Z", &ts);
	const auto nanoseconds = ts.nanos();

	std::cout << "1972-01-01T10:00:20.021Z in nanoseconds: " << nanoseconds << "\n";
	std::cout << "PROTOBUF_CPP_VERSION_STRING: " << PROTOBUF_CPP_VERSION_STRING << "\n";
	return EXIT_SUCCESS;
}
