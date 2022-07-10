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
    clock.getElapsedTime().asSeconds();

#ifdef SFML_WITH_WINDOW
    sf::VideoMode videoMode(720, 480);
#endif

#ifdef SFML_WITH_GRAPHICS
    sf::RectangleShape shape;
    shape.setFillColor(sf::Color::Cyan);
#endif

#ifdef SFML_WITH_NETWORK
    sf::TcpListener listener;
    listener.isBlocking();
#endif

#ifdef SFML_WITH_AUDIO
    sf::SoundBuffer buffer;
    sf::Sound sound;
    sound.setBuffer(buffer);
#endif

    return 0;
}
