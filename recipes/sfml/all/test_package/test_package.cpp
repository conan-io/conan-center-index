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
    std::cout << "Seconds elapsed: "
              << clock.getElapsedTime().asSeconds()
              << std::endl;

#ifdef SFML_WITH_WINDOW
 #if SFML_VERSION_MAJOR >= 3
    sf::VideoMode videoMode({720, 480});
 #else
    sf::VideoMode videoMode(720, 480);
 #endif
#endif

#ifdef SFML_WITH_GRAPHICS
    sf::RectangleShape shape;
    shape.setFillColor(sf::Color::Cyan);
#endif

#ifdef SFML_WITH_NETWORK
    sf::TcpListener listener;
    std::cout << "TCP blocking: "
              << listener.isBlocking()
              << std::endl;
#endif

#ifdef SFML_WITH_AUDIO
    sf::SoundBuffer buffer;
    sf::Sound sound(buffer);
#endif

    return 0;
}
