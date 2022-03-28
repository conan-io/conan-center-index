#define _CRT_SECURE_NO_WARNINGS

#include <gs/binary.h>
#include <cassert>
#include <iostream>

using namespace std;


// Example for serializing a POD type (without references/pointers since memory addresses change)
struct Vector3 {
	float x, y, z;

	void print() const {
		std::cout <<
			"x: " << x << '\n' <<
			"x: " << y << '\n' <<
			"y: " << z << '\n';
	}
};

namespace gs
{
template<typename Stream>
void serialize(Stream& stream, Vector3& value) {
	gs::read_or_write_bytes(stream, value);
}
}


// example class
struct A
{
	int x = 0;
	float y = 0;
	char z[3];
	Vector3 vec3;

	void print() const {
		cout
			<< "x: " << x << '\n'
			<< "x: " << y << '\n'
			<< "z: " << z << '\n'
			<< "vec3:\n";
		vec3.print();

	}
};

namespace gs
{
	//TODO alternatively can be a member function so we don't have to pass A and we can access members directly. Requires using SFINAE to check if the method is available.
	template<typename Stream>
	void serialize(Stream& stream, A& value) {
		// choose which members to serialize
		gs::serializer(stream, value.x, value.y, value.z, value.vec3);	// members' types' already have serialization implemented
	}
}


#include <gs/serializer.h>


namespace test
{
	void serialization()
	{
		A a;

		a.x = 5;
		a.y = 7.5;
		a.z[0] = 'a';
		a.z[1] = 'b';
		a.z[2] = '\0';
		a.vec3 = { 1,2,3 };

		puts("writing:");
		puts("========");
		a.print();
		putchar('\n');

		// serialize to file
		{
			ofstream f("test", ofstream::binary);
			gs::serializer(f, a);
		}

		a.x = 0;
		a.y = 0;
		a.z[0] = '0';
		a.z[1] = '0';
		a.vec3 = { 0,0,0 };

		// read back from file
		{
			ifstream f("test", ios::binary);
			gs::serializer(f, a);
		}

		puts("reading:");
		puts("========");
		a.print();
		putchar('\n');

		assert(a.x == 5);
		assert(a.y == 7.5);
		assert(a.z[0] == 'a');
		assert(a.z[1] == 'b');
		assert(a.z[2] == '\0');
		assert(a.vec3.x == 1);
		assert(a.vec3.y == 2);
		assert(a.vec3.z == 3);
	}
}


int main()
{
	puts("Serialization test");
	puts("==================");

	test::serialization();
}
