#include <fcntl.h>
#include <unistd.h>
#include <err.h>
#include <sys/stat.h>
#include <string.h>
#include <sys/types.h>
#include <stdint.h>

/*This is effectively a remake of the cat command which can be utilized on linux command line. The only difference being it primarily 
serves to print out contents from a specified source (- for stdin, or filename for a file) to std out.*/

void copyToStdout(int16_t source, char source_name[], uint16_t buf[], size_t count) { //copyFileToStdout copies the contents of the requested source to standard out
    ssize_t read_bytes;
    while((read_bytes=read(source, buf, count)) > 0) { // attempt to read count amount of bytes into buf from the source, stop when no more bytes can be read or if error occurs
        ssize_t written_bytes = write(STDOUT_FILENO, buf, read_bytes); // attempt to write the number of read_bytes and store how many were written to written_bytes

        if(written_bytes < 0) { // our call to write() failed, warn
            warn("%s", source_name);
        }

        while(written_bytes > 0 && written_bytes < read_bytes) { // if most recent write wrote bytes but could not write # of read bytes from buffer, attempt to write remaining bytes
            uint8_t bytesleft = read_bytes-written_bytes;
            written_bytes = written_bytes + write(STDOUT_FILENO, buf, bytesleft); //try to write # of bytesleft and update written_bytes to be number of total bytes written
            if((read_bytes-written_bytes) < bytesleft) { //if the most recent write failed, previous bytesleft will be geater than updated # of remaining bytes, warn
                warn("%s", source_name);
            }
        }
    }
    if(read_bytes < 0) { // if read failed/errored, warn
        warn("%s", source_name);
    }
    return;
}

int main(int argc, char *argv[]) {
    //intialize const values
    uint16_t buf[4096];
    size_t count = sizeof(buf);

    if (argc < 2) { //check to see if no arguments passed, call on copyToStdout with arg to read from stdin
        copyToStdout(STDIN_FILENO, "-", buf, count);
        return 0;
    }
    
    for(size_t i = argc-1; i>0; --i) { //one or more passed arguments, start parsing through in reverse order
        if(strcmp(argv[i], "-") == 0) { //check for -, if seen, call on copyToStdout with arg to read from stdin
            copyToStdout(STDIN_FILENO, "-", buf, count);
        } else { //no - seen, check to see if file can be opened successfully
            int16_t fd = open(argv[i], O_RDONLY);
            if (fd < 0) { 
                warn(argv[i], NULL); //error in opening file, warn
            } else {
                copyToStdout(fd, argv[i], buf, count); //file opened successfully, call on copyToStdout with arg to read from fd
                close(fd);
            }
        }
    }
    return 0;
}
