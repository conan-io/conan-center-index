#include <cstdlib>
#include <iostream>

#if protobuf_LITE != ON
#  include <google/protobuf/timestamp.pb.h>
#  include <google/protobuf/util/time_util.h>
#  include "addressbook.pb.h"
#else
#  include "addressbook-lite.pb.h"
#endif


int main()
{
    // example from https://protobuf.dev/getting-started/cpptutorial/
    tutorial::AddressBook address_book;
    tutorial::Person* person = address_book.add_people();
    person->set_email("a@b.c");
    tutorial::Person::PhoneNumber* phone_number = person->add_phones();
    phone_number->set_number("123");
    
    std::vector<char> buffer(address_book.ByteSizeLong());
    address_book.SerializeToArray(buffer.data(), static_cast<int>(buffer.size()));

    tutorial::AddressBook address_book2;
    address_book2.ParseFromArray(buffer.data(), static_cast<int>(buffer.size()));

#if protobuf_LITE != ON
	google::protobuf::Timestamp ts;
	google::protobuf::util::TimeUtil::FromString("1972-01-01T10:00:20.021Z", &ts);
	const auto nanoseconds = ts.nanos();
	std::cout << "1972-01-01T10:00:20.021Z in nanoseconds: " << nanoseconds << "\n";
#endif
	return EXIT_SUCCESS;
}
