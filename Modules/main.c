/* Python interpreter main program */

#include "Python.h"
#include "osdefs.h"

#ifdef HAVE_UNISTD_H
#include <unistd.h>
#endif

#ifdef MS_WINDOWS
#include <fcntl.h>
#endif

#if defined(PYOS_OS2) || defined(MS_WINDOWS)
#define PYTHONHOMEHELP "<prefix>\\lib"
#else
#define PYTHONHOMEHELP "<prefix>/python2.0"
#endif

#include "pygetopt.h"

#define COPYRIGHT \
    "Type \"copyright\", \"credits\" or \"license\" for more information."

/* For Py_GetArgcArgv(); set by main() */
static char **orig_argv;
static int  orig_argc;

/* Short usage message (with %s for argv0) */
static char *usage_line =
"usage: %s [option] ... [-c cmd | file | -] [arg] ...\n";

/* Long usage message, split into parts < 512 bytes */
static char *usage_top = "\
Options and arguments (and corresponding environment variables):\n\
-d     : debug output from parser (also PYTHONDEBUG=x)\n\
-i     : inspect interactively after running script, (also PYTHONINSPECT=x)\n\
         and force prompts, even if stdin does not appear to be a terminal\n\
-O     : optimize generated bytecode (a tad; also PYTHONOPTIMIZE=x)\n\
-OO    : remove doc-strings in addition to the -O optimizations\n\
-S     : don't imply 'import site' on initialization\n\
-t     : issue warnings about inconsistent tab usage (-tt: issue errors)\n\
";
static char *usage_mid = "\
-u     : unbuffered binary stdout and stderr (also PYTHONUNBUFFERED=x)\n\
-U     : Unicode literals: treats '...' literals like u'...'\n\
-v     : verbose (trace import statements) (also PYTHONVERBOSE=x)\n\
-x     : skip first line of source, allowing use of non-Unix forms of #!cmd\n\
-h     : print this help message and exit\n\
-V     : print the Python version number and exit\n\
-W arg : warning control (arg is action:message:category:module:lineno)\n\
-c cmd : program passed in as string (terminates option list)\n\
file   : program read from script file\n\
-      : program read from stdin (default; interactive mode if a tty)\n\
";
static char *usage_bot = "\
arg ...: arguments passed to program in sys.argv[1:]\n\
Other environment variables:\n\
PYTHONSTARTUP: file executed on interactive startup (no default)\n\
PYTHONPATH   : '%c'-separated list of directories prefixed to the\n\
               default module search path.  The result is sys.path.\n\
PYTHONHOME   : alternate <prefix> directory (or <prefix>%c<exec_prefix>).\n\
               The default module search path uses %s.\n\
PYTHONCASEOK : ignore case in 'import' statements (Windows).\n\
";


static void
usage(int exitcode, char* program)
{
	fprintf(stderr, usage_line, program);
	fprintf(stderr, usage_top);
	fprintf(stderr, usage_mid);
	fprintf(stderr, usage_bot, DELIM, DELIM, PYTHONHOMEHELP);
	exit(exitcode);
	/*NOTREACHED*/
}


/* Main program */

DL_EXPORT(int)
Py_Main(int argc, char **argv)
{
	int c;
	int sts;
	char *command = NULL;
	char *filename = NULL;
	FILE *fp = stdin;
	char *p;
	int inspect = 0;
	int unbuffered = 0;
	int skipfirstline = 0;
	int stdin_is_interactive = 0;
	int help = 0;
	int version = 0;

	orig_argc = argc;	/* For Py_GetArgcArgv() */
	orig_argv = argv;

	if ((p = getenv("PYTHONINSPECT")) && *p != '\0')
		inspect = 1;
	if ((p = getenv("PYTHONUNBUFFERED")) && *p != '\0')
		unbuffered = 1;

	PySys_ResetWarnOptions();

	while ((c = _PyOS_GetOpt(argc, argv, "c:diOStuUvxXhVW:")) != EOF) {
		if (c == 'c') {
			/* -c is the last option; following arguments
			   that look like options are left for the
			   the command to interpret. */
			command = malloc(strlen(_PyOS_optarg) + 2);
			if (command == NULL)
				Py_FatalError(
				   "not enough memory to copy -c argument");
			strcpy(command, _PyOS_optarg);
			strcat(command, "\n");
			break;
		}
		
		switch (c) {

		case 'd':
			Py_DebugFlag++;
			break;

		case 'i':
			inspect++;
			Py_InteractiveFlag++;
			break;

		case 'O':
			Py_OptimizeFlag++;
			break;

		case 'S':
			Py_NoSiteFlag++;
			break;

		case 't':
			Py_TabcheckFlag++;
			break;

		case 'u':
			unbuffered++;
			break;

		case 'v':
			Py_VerboseFlag++;
			break;

		case 'x':
			skipfirstline = 1;
			break;

		case 'U':
			Py_UnicodeFlag++;
			break;
		case 'h':
			help++;
			break;
		case 'V':
			version++;
			break;

		case 'W':
			PySys_AddWarnOption(_PyOS_optarg);
			break;

		/* This space reserved for other options */

		default:
			usage(2, argv[0]);
			/*NOTREACHED*/

		}
	}

	if (help)
		usage(0, argv[0]);

	if (version) {
		fprintf(stderr, "Python %s\n", PY_VERSION);
		exit(0);
	}

	if (command == NULL && _PyOS_optind < argc &&
	    strcmp(argv[_PyOS_optind], "-") != 0)
	{
		filename = argv[_PyOS_optind];
		if (filename != NULL) {
			if ((fp = fopen(filename, "r")) == NULL) {
				fprintf(stderr, "%s: can't open file '%s'\n",
					argv[0], filename);
				exit(2);
			}
			else if (skipfirstline) {
				int ch;
				/* Push back first newline so line numbers
				   remain the same */
				while ((ch = getc(fp)) != EOF) {
					if (ch == '\n') {
						(void)ungetc(ch, fp);
						break;
					}
				}
			}
		}
	}

	stdin_is_interactive = Py_FdIsInteractive(stdin, (char *)0);

	if (unbuffered) {
#ifdef MS_WINDOWS
		_setmode(fileno(stdin), O_BINARY);
		_setmode(fileno(stdout), O_BINARY);
#endif
#ifndef MPW
#ifdef HAVE_SETVBUF
		setvbuf(stdin,  (char *)NULL, _IONBF, BUFSIZ);
		setvbuf(stdout, (char *)NULL, _IONBF, BUFSIZ);
		setvbuf(stderr, (char *)NULL, _IONBF, BUFSIZ);
#else /* !HAVE_SETVBUF */
		setbuf(stdin,  (char *)NULL);
		setbuf(stdout, (char *)NULL);
		setbuf(stderr, (char *)NULL);
#endif /* !HAVE_SETVBUF */
#else /* MPW */
		/* On MPW (3.2) unbuffered seems to hang */
		setvbuf(stdin,  (char *)NULL, _IOLBF, BUFSIZ);
		setvbuf(stdout, (char *)NULL, _IOLBF, BUFSIZ);
		setvbuf(stderr, (char *)NULL, _IOLBF, BUFSIZ);
#endif /* MPW */
	}
	else if (Py_InteractiveFlag) {
#ifdef MS_WINDOWS
		/* Doesn't have to have line-buffered -- use unbuffered */
		/* Any set[v]buf(stdin, ...) screws up Tkinter :-( */
		setvbuf(stdout, (char *)NULL, _IONBF, BUFSIZ);
#else /* !MS_WINDOWS */
#ifdef HAVE_SETVBUF
		setvbuf(stdin,  (char *)NULL, _IOLBF, BUFSIZ);
		setvbuf(stdout, (char *)NULL, _IOLBF, BUFSIZ);
#endif /* HAVE_SETVBUF */
#endif /* !MS_WINDOWS */
		/* Leave stderr alone - it should be unbuffered anyway. */
  	}

	Py_SetProgramName(argv[0]);
	Py_Initialize();

	if (Py_VerboseFlag ||
	    (command == NULL && filename == NULL && stdin_is_interactive))
		fprintf(stderr, "Python %s on %s\n%s\n",
			Py_GetVersion(), Py_GetPlatform(), COPYRIGHT);
	
	
	if (command != NULL) {
		/* Backup _PyOS_optind and force sys.argv[0] = '-c' */
		_PyOS_optind--;
		argv[_PyOS_optind] = "-c";
	}

	PySys_SetArgv(argc-_PyOS_optind, argv+_PyOS_optind);

	if ((inspect || (command == NULL && filename == NULL)) &&
	    isatty(fileno(stdin))) {
		PyObject *v;
		v = PyImport_ImportModule("readline");
		if (v == NULL)
			PyErr_Clear();
		else
			Py_DECREF(v);
	}

	if (command) {
		sts = PyRun_SimpleString(command) != 0;
		free(command);
	}
	else {
		if (filename == NULL && stdin_is_interactive) {
			char *startup = getenv("PYTHONSTARTUP");
			if (startup != NULL && startup[0] != '\0') {
				FILE *fp = fopen(startup, "r");
				if (fp != NULL) {
					(void) PyRun_SimpleFile(fp, startup);
					PyErr_Clear();
					fclose(fp);
				}
			}
		}
		sts = PyRun_AnyFileEx(
			fp,
			filename == NULL ? "<stdin>" : filename,
			filename != NULL) != 0;
	}

	if (inspect && stdin_is_interactive &&
	    (filename != NULL || command != NULL))
		sts = PyRun_AnyFile(stdin, "<stdin>") != 0;

	Py_Finalize();

#ifdef __INSURE__
	/* Insure++ is a memory analysis tool that aids in discovering
	 * memory leaks and other memory problems.  On Python exit, the
	 * interned string dictionary is flagged as being in use at exit
	 * (which it is).  Under normal circumstances, this is fine because
	 * the memory will be automatically reclaimed by the system.  Under
	 * memory debugging, it's a huge source of useless noise, so we
	 * trade off slower shutdown for less distraction in the memory
	 * reports.  -baw
	 */
	_Py_ReleaseInternedStrings();
#endif /* __INSURE__ */

	return sts;
}


/* Make the *original* argc/argv available to other modules.
   This is rare, but it is needed by the secureware extension. */

void
Py_GetArgcArgv(int *argc, char ***argv)
{
	*argc = orig_argc;
	*argv = orig_argv;
}
