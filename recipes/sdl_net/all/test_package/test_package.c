#define SDL_MAIN_HANDLED
#include <SDL_net.h>
#include <SDL.h>

#include <stdio.h>

int main(int argc, char **argv)
{
	IPaddress ip;
	const char *host;
	Uint8 *ipaddr;

	/* check our commandline */
	if (argc < 2) 
	{
		fprintf(stderr, "Need at least one argument\n");
		exit(1);
	}

	/* initialize SDL */
	if(SDL_Init(0)==-1)
	{
		fprintf(stderr, "SDL_Init: %s\n",SDL_GetError());
		exit(2);
	}

	/* initialize SDL_net */
	if(SDLNet_Init()==-1)
	{
		fprintf(stderr, "SDLNet_Init: %s\n",SDLNet_GetError());
		exit(3);
	}

	/* Resolve the argument into an IPaddress type */
	printf("Resolving %s\n",argv[1]);
	if(SDLNet_ResolveHost(&ip,argv[1],0)==-1)
	{
		fprintf(stderr, "Could not resolve host \"%s\"\n%s\n",argv[1],SDLNet_GetError());
		exit(4);
	}

	/* use the IP as a Uint8[4] */
	ipaddr=(Uint8*)&ip.host;

	/* output the IP address nicely */
	printf("IP Address : %d.%d.%d.%d\n",
			ipaddr[0], ipaddr[1], ipaddr[2], ipaddr[3]);

	/* resolve the hostname for the IPaddress */
	host=SDLNet_ResolveIP(&ip);

	/* print out the hostname we got */
	if(host)
		printf("Hostname   : %s\n",host);
	else
		printf("No Hostname found\n");

	/* shutdown SDL_net */
	SDLNet_Quit();

	/* shutdown SDL */
	SDL_Quit();

	return(0);
}
