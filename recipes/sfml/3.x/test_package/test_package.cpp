#include <iostream>

#include <SFML/System.hpp>

#ifdef SFML_WITH_WINDOW
#include <SFML/Window.hpp>
#endif
#ifdef SFML_WITH_GRAPHICS
#include <SFML/Graphics.hpp>
#endif
#ifdef SFML_WITH_NETWORK
#include <SFML/Network.hpp>
#endif
#ifdef SFML_WITH_AUDIO
#include <SFML/Audio.hpp>
#endif

int main()
{
    sf::Clock clock;

#ifdef SFML_WITH_WINDOW
    sf::VideoMode videoMode{};
    std::cout << "Video mode: " << &videoMode << std::endl;
    std::cout << "Vulkan supported: " << sf::Vulkan::isAvailable() << std::endl;
#endif

#ifdef SFML_WITH_GRAPHICS
    sf::RectangleShape shape;
    shape.setFillColor(sf::Color::Cyan);
    std::cout << "Shape fill color - R: " << static_cast<int>(shape.getFillColor().r)
              << ", G: " << static_cast<int>(shape.getFillColor().g)
              << ", B: " << static_cast<int>(shape.getFillColor().b) << std::endl;
#endif

#ifdef SFML_WITH_NETWORK
    sf::TcpListener listener;
    std::cout << "Is tcp listener blocking?: " << listener.isBlocking() << std::endl;
#endif

#ifdef SFML_WITH_AUDIO
    sf::SoundBuffer buffer;
    sf::Sound sound(buffer);
    std::cout << "Sound status: " << static_cast<int>(sound.getStatus()) << std::endl;
#endif

    std::cout << "Test elapsed time: " << clock.getElapsedTime().asSeconds() << std::endl;

    return 0;
}
