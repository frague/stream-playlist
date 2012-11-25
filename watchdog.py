#!/usr/bin/python

import os, glob
try:
    import fcntl
    read_stdout = True
except:
    read_stdout = False

from logger import make_custom_logger
from subprocess import call, Popen, PIPE
from time import sleep
import mutagen

if __name__ == "__main__":
    LOGGER = make_custom_logger()

    search_dir = "./dubsteplight/"
    stream_url = "http://dubsteplight.moeradio.ru:23000/dubsteplight.ogg"
    forbidden_chars = ["/", "\\"]

    LOGGER.info("Starting stream %s parsing" % stream_url)

    ripper = Popen(["streamripper", stream_url], stdout=PIPE)
    if read_stdout:
        fcntl.fcntl(ripper.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

    newest = None
    converted = 0
    try:
        while True:
            files = filter(os.path.isfile, glob.glob(search_dir + "*.ogg"))
            files.sort(key=lambda x: os.path.getmtime(x))

            if read_stdout:
                while True:
                    try:
                        LOGGER.debug(ripper.stdout.readline().rstrip())
                    except IOError:
                        break
        
            if len(files):
                for f in files:
                    if f == newest:
                        break
                    (artist, title) = mutagen.File(f)["title"][0].split(" - ", 1)
                    LOGGER.info("Media processing: %s (%s)" % (title, artist))
                
                    name ="%s - %s.mp3" % (artist, title)
                    for char in forbidden_chars:
                        name = name.replace(char, "-")
                    name = "%s%s" % (search_dir, name)

                    if not os.path.exists(name):
                        call(["sox", "-S", f, name])

                        LOGGER.debug("ID3 tags for '%s' transferring" % name)
                        audio = mutagen.easyid3.EasyID3(name)
                        audio["artist"] = artist
                        audio["title"] = title
                        audio["encodedby"] = u"Stream playlist generator"
                        audio.save()
                        converted += 1
                    else:
                        LOGGER.info("MP3 file (%s) already exists" % name)

                    LOGGER.debug("Source '%s' removing" % f)
                    os.remove(f)
                newest = files[0]
                LOGGER.info("%s new tracks converted so far" % converted)
            sleep(5)
    except KeyboardInterrupt:
        ripper.kill()
        pass
