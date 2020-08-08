#include <cstdlib>
#include <iostream>

#include <SFML/System.hpp>

#ifdef WITH_WINDOW
    #include <SFML/Window.hpp>
#endif
#ifdef WITH_GRAPHICS
    #include <SFML/Graphics.hpp>
#endif
#ifdef WITH_AUDIO
    #include <SFML/Audio.hpp>
#endif
#ifdef WITH_NETWORK
    #include <SFML/Network.hpp>
#endif


int main(int argc, char **argv)
{
    sf::Clock clock;
    clock.getElapsedTime().asSeconds();

    #ifdef WITH_WINDOW
        sf::VideoMode videoMode(720, 480);
    #endif

    #ifdef WITH_GRAPHICS
        sf::RectangleShape shape;
        shape.setFillColor(sf::Color::Cyan);
    #endif

    #ifdef WITH_AUDIO
        sf::SoundBuffer buffer;
        sf::Sound sound;
        sound.setBuffer(buffer);
    #endif

    #ifdef WITH_NETWORK
        sf::TcpListener listener;
        listener.isBlocking();
    #endif

    return EXIT_SUCCESS;
}
