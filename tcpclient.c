/**
* @author Edward Conn
*/
#include <argp.h>
#include <netdb.h> 
#include <stdio.h> 
#include <stdlib.h> 
#include <string.h> 
#include <sys/socket.h>
#include <unistd.h>

#include "opt_parser.h"

#define ADDRESS  "127.0.0.1"
#define MAX 256 //Read write buffer size

int main(int argc, char **argv)
{
    FILE *outstream;
	struct arguments arguments;
    /* Set argument defaults */
	arguments.outfile = NULL;
	arguments.verbose = 0; 
	arguments.port = 50000;
	arguments.verbose = 0;
    
    /* Parse our arguments; every option seen by parse_opt will
     be reflected in arguments. */
    //argp_parse (&argp, argc, argv, 0, 0, arguments);
	outstream = arguments.outfile ? fopen (arguments.outfile, "w") : stdout;

	if (arguments.verbose)
	{
		//TODO: Add debug output print
	}

	int port = arguments.port > 0 ? arguments.port : 5000 ;

	//AF_INET IPV4 domain const
	//SOCK_STREAM TCP constant
	// Internet protocal 0
	int sockfd = socket(AF_INET , SOCK_STREAM, 0);
	bind(sockfd, (struct sockaddr *) ADDRESS, sizeof(ADDRESS));
	connect(sockfd, (struct sockaddr *) ADDRESS, sizeof(ADDRESS));
	
    int n = 0;
    char buff[MAX];
	while(strncmp(buff, "exit", 4) != 0) { 
		//Null buffer
		bzero(buff, sizeof(buff)); 
		// For testing
		{
            printf("Enter the string : ");
            while ((buff[n++] = getchar()) != '\n'); 
            write(sockfd, buff, sizeof(buff));
            //Clean buffer before read
            bzero(buff, sizeof(buff)); 
            read(sockfd, buff, sizeof(buff)); 
            printf("From Server : %s", buff);
        }
        n = 0;
	} 
	close(sockfd);
	return 0;
}

