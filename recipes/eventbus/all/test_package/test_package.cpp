
#include <dexode/EventBus.hpp>


using namespace dexode;

namespace event
{

struct Value
{
	int value{-1};
};

}


int main(void) {
	EventBus bus;
	auto listener = EventBus::Listener::createNotOwning(bus);

	int callCount = 0;

	listener.listen([&](const event::Value& event) {
		++callCount;
	});

	bus.postpone(event::Value{3});
    bus.process();

    
    return 0;
}
