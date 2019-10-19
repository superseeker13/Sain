/**
* @author Edward Conn
*/
#include <argp.h>
#include <stdlib.h>
#include <stdio.h>

const char *argp_program_version = "argp-ex3 1.0";
const char *argp_program_bug_address = "<bug-gnu-utils@gnu.org>";

//Documentation
static char doc[] = "TCP client with options and arguments using argp";
static char args_doc[] = "ARG1 ARG2";

/* The options we understand. */
static struct argp_option options[] = {
  {"verbose",  'v', 0,      0,  "Produce verbose output" },
  {"output",   'o', "FILE", 0, "Output to File" },
  {"port",   'p', "FILE", 0, "Port number" },
  { 0 }
};

struct arguments
{
	char *args[2]; /* ARG1 and ARG2 */
	char *outfile; /* Argument for -o */
	int verbose;   /* The -v flag */
	int port;      /* -p portnumber */
};

/* Parse a single option. */
static error_t parse_opt (int key, char *arg, struct argp_state *state)
{
  /* Get the input argument from argp_parse, which we
     know is a pointer to our arguments structure. */
  struct arguments *arguments = state->input;

  switch (key)
  {
    case 'v':
      arguments->verbose = 1;
      break;
    case 'o':
      arguments->outfile = arg;
      break;
    case 'p':
      arguments->port = atoi(arg);
      break;

    case ARGP_KEY_ARG:
      if(state->arg_num >= 2){
        argp_usage (state);
        }
      arguments->args[state->arg_num] = arg;
      break;

    case ARGP_KEY_END:
      if (state->arg_num < 2)
        /* Not enough arguments. */
        argp_usage (state);
      break;

    default:
      return ARGP_ERR_UNKNOWN;
    }
  return 0;
}

static struct argp argp = { options, parse_opt, args_doc, doc };
