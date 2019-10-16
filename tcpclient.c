/**
* @author Edward Conn
*/
#include <argp.h>
#include <stdio.h>
#include <string.h> 
#include <sys/socket.h>

#define MAX = 255 //Read write buffer size
#define ERROR = -1

struct arguments
{
	char *args[2]; /* ARG1 and ARG2 */
	char *outfile; /* Argument for -o */
	int verbose;   /* The -v flag */
	int port;      /* -p portnumber */
	char *addressstr;  /* Arguments for -a */
};

int main(int argc, char const *argv[])
{
	struct arguments arguments;
	FILE *outstream;

	/* Set argument defaults */
	arguments.outfile = NULL;
	arguments.verbose = 0; 
	arguments.port = 50000;
	arguments.addressstr = "127.0.0.1"; 
	arguments.verbose = 0;

	argp_parse (&argp, argc, argv, 0, 0, &arguments);
	outstream =  arguments.outfile ? fopen (arguments.outfile, "w") : stdout;

	fprintf (outstream, "ARG1 = %s\nARG2 = %s\n\n",
	arguments.args[0],
	arguments.args[1]);

	if (arguments.verbose)
	{
		//TODO: Add debug output print
	}

	// Address must be a standard IPV4 
	char *address = arguments.addressstr ? arguments.addressstr : "127.0.0.1";
	// Port <= 6000
	int port = arguments.port > 0 ? arguments.port : 5000 ;

	//AF_INET IPV4 domain const
	//SOCK_STREAM TCP constant
	// Internet protocal 0
	int sockfd = socket(AF_INET , SOCK_STREAM, 0)
	// optional int setsockopt(int sockfd, int level, int optname, const void *optval, socklen_t optlen);
	bind(sockfd, (struct sockaddr *) ADDRESS, sizeof(ADDRESS));
	connect(sockfd, (struct sockaddr *) ADDRESS, sizeof(ADDRESS));
	
	for (int n = 0, char buff[MAX]; strncmp(buff, "exit", 4)) != 0; n = 0) { 
		//Null buffer
		bzero(buff, sizeof(buff)); 
		// For testing
		//printf("Enter the string : ");
		while ((buff[n++] = getchar()) != '\n'); 
		write(sockfd, buff, sizeof(buff));
		//Clean buffer before read
		bzero(buff, sizeof(buff)); 
		read(sockfd, buff, sizeof(buff)); 
		printf("From Server : %s", buff); 
	} 
	sockfd.close();
	
	return 0;
}
