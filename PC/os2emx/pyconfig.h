#ifndef Py_CONFIG_H
#define Py_CONFIG_H

/*
   config.h.
   At some time in the past, generated automatically by configure.
   Maintained manually for better results.
*/

#define PLATFORM	"os2emx"
#define COMPILER	"[EMX GCC " __VERSION__ "]"
#define PYOS_OS2
#define PYCC_GCC
#define PREFIX		"/usr"

/* Debugging */
#ifndef Py_DEBUG
/*#define Py_DEBUG 1*/
#endif

/* so that emx socket headers will define IP V4 socket types */
#define TCPIPV4

/* Use OS/2 flavour of threads */
#define WITH_THREAD
#define OS2_THREADS

/* We want sockets */
#define USE_SOCKET
#define socklen_t int

/* enable the GC module */
#define WITH_CYCLE_GC	1

/* Unicode related */
#define Py_USING_UNICODE
#define PY_UNICODE_TYPE    wchar_t
#define Py_UNICODE_SIZE SIZEOF_SHORT

/* enable the Python object allocator */
/*#define	WITH_PYMALLOC	1*/

#define PYTHONPATH  ".;./Lib;./Lib/plat-" PLATFORM ";./Lib/lib-dynload;./Lib/site-packages"

#define HAVE_TTYNAME	1
#define HAVE_WAIT	1
#define HAVE_GETEGID    1
#define HAVE_GETEUID    1
#define HAVE_GETGID     1
#define HAVE_GETPPID    1
#define HAVE_GETUID     1
#define HAVE_OPENDIR    1
#define HAVE_PIPE       1
#define HAVE_POPEN      1
#define HAVE_SYSTEM	1
#define HAVE_TTYNAME	1
#define HAVE_DYNAMIC_LOADING	1

/* if port of GDBM installed, it includes NDBM emulation */
#define HAVE_NDBM_H	1

/* need this for spawnv code in posixmodule (cloned from WIN32 def'n) */
typedef long intptr_t;

/* we don't have tm_zone but do have the external array
   tzname.  */
#define HAVE_TZNAME 1

/* Define as the return type of signal handlers (int or void).  */
#define RETSIGTYPE void

/* Define if you have the ANSI C header files.  */
#define STDC_HEADERS 1

/* Define if you can safely include both <sys/time.h> and <time.h>.  */
#define TIME_WITH_SYS_TIME 1

/* Used for BeOS configuration */
/* #undef DL_EXPORT_HEADER */
#ifdef DL_EXPORT_HEADER
#include DL_EXPORT_HEADER
#endif

/* Define this if you have the type long long */
#define HAVE_LONG_LONG 1

/* Define if your compiler supports function prototypes */
#define HAVE_PROTOTYPES 1

/* Define if your compiler supports variable length function prototypes
   (e.g. void fprintf(FILE *, char *, ...);) *and* <stdarg.h> */
#define HAVE_STDARG_PROTOTYPES 1

/* Define if malloc(0) returns a NULL pointer */
#define MALLOC_ZERO_RETURNS_NULL 1

/* Define to force use of thread-safe errno, h_errno, and other functions */
#define _REENTRANT 1

/* Define if  you can safely include both <sys/select.h> and <sys/time.h>
   (which you can't on SCO ODT 3.0). */
#define SYS_SELECT_WITH_SYS_TIME 1

/* The number of bytes in an off_t. */
#define SIZEOF_OFF_T 4

/* The number of bytes in an time_t. */
#define SIZEOF_TIME_T 4

/* The number of bytes in a short.  */
#define SIZEOF_SHORT 2

/* The number of bytes in a int.  */
#define SIZEOF_INT 4

/* The number of bytes in a long.  */
#define SIZEOF_LONG 4

/* The number of bytes in a long long.  */
#define SIZEOF_LONG_LONG 8

/* The number of bytes in a void *.  */
#define SIZEOF_VOID_P 4

/* Define if you have the alarm function.  */
#define HAVE_ALARM 1

/* Define if you have the clock function.  */
#define HAVE_CLOCK 1

/* Define if you have the dup2 function.  */
#define HAVE_DUP2 1

/* Define if you have the execv function.  */
#define HAVE_EXECV 1

/* Define if you have the spawnv function.  */
#define HAVE_SPAWNV 1

/* Define if you have the flock function.  */
#define HAVE_FLOCK 1

/* Define if you have the fork function.  */
#define HAVE_FORK 1

/* Define if you have the fsync function.  */
#define HAVE_FSYNC 1

/* Define if you have the ftime function.  */
#define HAVE_FTIME 1

/* Define if you have the ftruncate function.  */
#define HAVE_FTRUNCATE 1

/* Define if you have the getcwd function.  */
#define HAVE_GETCWD 1

/* Define if you have the getpeername function.  */
#define HAVE_GETPEERNAME 1

/* Define if you have the getpgrp function.  */
#define HAVE_GETPGRP 1

/* Define if you have the getpid function.  */
#define HAVE_GETPID 1

/* Define if you have the getpwent function.  */
#define HAVE_GETPWENT 1

/* Define if you have the gettimeofday function.  */
#define HAVE_GETTIMEOFDAY 1

/* Define if you have the getwd function.  */
#define HAVE_GETWD 1

/* Define if you have the hypot function.  */
#define HAVE_HYPOT 1

/* Define if you have the kill function.  */
#define HAVE_KILL 1

/* Define if you have the memmove function.  */
#define HAVE_MEMMOVE 1

/* Define if you have the mktime function.  */
#define HAVE_MKTIME 1

/* Define if you have the pause function.  */
#define HAVE_PAUSE 1

/* Define if you have the putenv function.  */
#define HAVE_PUTENV 1

/* Define if you have the select function.  */
#define HAVE_SELECT 1

/* Define if you have the setgid function.  */
#define HAVE_SETGID 1

/* Define if you have the setlocale function.  */
#define HAVE_SETLOCALE 1

/* Define if you have the setpgid function.  */
#define HAVE_SETPGID 1

/* Define if you have the setuid function.  */
#define HAVE_SETUID 1

/* Define if you have the setvbuf function.  */
#define HAVE_SETVBUF 1

/* Define if you have the sigaction function.  */
#define HAVE_SIGACTION 1

/* Define if you have the strdup function.  */
#define HAVE_STRDUP 1

/* Define if you have the strerror function.  */
#define HAVE_STRERROR 1

/* Define if you have the strftime function.  */
#define HAVE_STRFTIME 1

/* Define if you have the strptime function.  */
#define HAVE_STRPTIME 1

/* Define if you have the tcgetpgrp function.  */
#define HAVE_TCGETPGRP 1

/* Define if you have the tcsetpgrp function.  */
#define HAVE_TCSETPGRP 1

/* Define if you have the times function.  */
#define HAVE_TIMES 1

/* Define if you have the truncate function.  */
#define HAVE_TRUNCATE 1

/* Define if you have the uname function.  */
#define HAVE_UNAME 1

/* Define if you have the waitpid function.  */
#define HAVE_WAITPID 1

/* Define if you have the <dirent.h> header file.  */
#define HAVE_DIRENT_H 1

/* Define if you have the <fcntl.h> header file.  */
#define HAVE_FCNTL_H 1

/* Define if you have the <limits.h> header file.  */
#define HAVE_LIMITS_H 1

/* Define if you have the <locale.h> header file.  */
#define HAVE_LOCALE_H 1

/* Define if you have the <ncurses.h> header file.  */
#define HAVE_NCURSES_H 1

/* Define if you have the <signal.h> header file.  */
#define HAVE_SIGNAL_H 1

/* Define if you have the <stdarg.h> header file.  */
#define HAVE_STDARG_H 1

/* Define if you have the <stddef.h> header file.  */
#define HAVE_STDDEF_H 1

/* Define if you have the <stdlib.h> header file.  */
#define HAVE_STDLIB_H 1

/* Define if you have the <sys/file.h> header file.  */
#define HAVE_SYS_FILE_H 1

/* Define if you have the <sys/param.h> header file.  */
#define HAVE_SYS_PARAM_H 1

/* Define if you have the <sys/select.h> header file.  */
#define HAVE_SYS_SELECT_H 1

/* Define if you have the <sys/time.h> header file.  */
#define HAVE_SYS_TIME_H 1

/* Define if you have the <sys/times.h> header file.  */
#define HAVE_SYS_TIMES_H 1

/* Define if you have the <sys/un.h> header file.  */
#define HAVE_SYS_UN_H 1

/* Define if you have the <sys/utsname.h> header file.  */
#define HAVE_SYS_UTSNAME_H 1

/* Define if you have the <sys/wait.h> header file.  */
#define HAVE_SYS_WAIT_H 1

/* Define if you have the <unistd.h> header file.  */
#define HAVE_UNISTD_H 1

/* Define if you have the <utime.h> header file.  */
#define HAVE_UTIME_H 1

/* EMX has an snprintf() */
#define HAVE_SNPRINTF

#endif /* !Py_CONFIG_H */

