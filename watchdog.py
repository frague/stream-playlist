#!/usr/bin/python

import os, glob
from logging import getLogger
from subprocess import call
from time import sleep
import mutagen

if __name__ == "__main__":
    LOGGER = getLogger()

    search_dir = "./dubsteplight/"

    newest = None 
    while True:
        files = filter(os.path.isfile, glob.glob(search_dir + "*.ogg"))
        files.sort(key=lambda x: os.path.getmtime(x))

        LOGGER.debug("Scanning for the new files...")
        if len(files):
            for f in files:
                if f == newest:
                    break
                (artist, title) = mutagen.File(f)["title"][0].split(" - ", 1)
                LOGGER.info("Media processing: %s (%s)" % (title, artist))
                
                name ="%s%s - %s.mp3" % (search_dir, artist, title)
                call(["sox", "-S", f, name])

                LOGGER.debug("ID3 tags for '%s' transferring" % name)
                audio = mutagen.easyid3.EasyID3(name)
                audio["artist"] = artist
                audio["title"] = title
                audio["encodedby"] = u"Stream playlist generator"
                audio.save()

                LOGGER.debug("Source '%s' removing" % f)
                os.remove(f)
            newest = files[0]
        sleep(5)

