#include <cstdlib>
#include <iostream>

#include <google/protobuf/timestamp.pb.h>
#include <google/protobuf/util/time_util.h>

#include "addressbook.pb.h"

int main()
{
	tutorial::Person p;
	p.set_id(21);
	p.set_name("conan-center-index");
	p.set_email("info@conan.io");

	google::protobuf::Timestamp ts;
	google::protobuf::util::TimeUtil::FromString("1972-01-01T10:00:20.021Z", &ts);
	const auto nanoseconds = ts.nanos();

	std::cout << nanoseconds << "\n";
	return EXIT_SUCCESS;
}
