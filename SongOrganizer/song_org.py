"""
This script was adapted from the one in http://bamos.github.io/2014/07/05/music-organizer/ by [Brandon Amos](http://bamos.github.io)
"""

import argparse
import glob
import os
import re
import shutil
import sys
import subprocess
from mutagen.easyid3 import EasyID3


# Maps a string such as 'The Beatles' to 'beatles'.
def toNeat(s):
    s = s.lower().replace("&", "and")

    # Put spaces between and remove blank characters.
    blankCharsPad = r"()\[\],.\\\?\#/\!\$\:\;"
    blankCharsNoPad = r"'\""
    s = re.sub(r"([" + blankCharsPad + r"])([^ ])", "\\1 \\2", s)
    s = re.sub("[" + blankCharsPad + blankCharsNoPad + "]", "", s)

    # replace all characters except alphanumeric with '-', '+', and '='
    s = re.sub("[^0-9a-zA-Z\-\+\=]", "-", s)

    # Replace spaces with a single dash.
    s = re.sub(r"[ \*\_]+", "-", s)
    s = re.sub("-+", "-", s)
    s = re.sub("^-*", "", s)
    s = re.sub("-*$", "", s)

    # Remove starting "The "
    if s.startswith("the-"):
        s = s.replace("the-", "")
    return s


def try_easyid3(filename):
    try:
        audio = EasyID3(filename)
        artist = audio['artist'][0].encode('ascii', 'ignore').decode("utf-8")
        title = audio['title'][0].encode('ascii', 'ignore').decode("utf-8")
    except:
        artist = None
        title = None
    return (artist, title)


def try_ffmpeg(filename):
    result = subprocess.run(['ffmpeg', '-i', filename, '-hide_banner'], capture_output=True)
    artist = None
    title = None
    for line in result.stderr.decode("utf-8").split("\n"):
        line = line.lower().strip()
        line = re.sub(r"[ \*\_]+", " ", line)
        if artist is None and line.startswith('artist : '):
            artist = line.split("artist : ")[1]
        elif title is None and line.startswith('title : '):
            title = line.split("title : ")[1]
    return (artist, title)
    


# Extracts information from filename, moves the song to targetDir, prints if verbose
def song(filename, targetDir, verbose):
    if filename[0] == '.':
        print("Ignoring dotfile: '{}'".format(filename))
        return
    ext = os.path.splitext(filename)[1]
    # For all mp3s
    (artist, title) = try_easyid3(filename)
    # For other files
    if artist is None:
        (artist, title) = try_ffmpeg(filename)
    # If not found
    if artist is None or title is None:
        print("ERROR: " + filename + " with missing artist or title")
        return
    neatArtist = toNeat(artist)
    neatTitle = toNeat(title)
    
    if not os.path.isdir(os.path.join(targetDir, neatArtist)):
        os.mkdir(os.path.join(targetDir, neatArtist))
    newFullPath = os.path.join(targetDir, neatArtist, neatTitle + ext)
    if os.path.isfile(newFullPath):
        print("ERROR: " + newFullPath + " already exists! Skipping " + filename)
        return
    if verbose:
        print(filename + " with artist " + artist + " and title " + title + " renamed to " + newFullPath)
    os.rename(filename, newFullPath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='''Organizes a music collection using tag information.
        The directory format is that the music collection consists of
        artist subdirectories.
        All names are made lowercase and separated by dashes for easier
        navigation in a Linux filesystem.'''
    )
    parser.add_argument('--from', default='raw', dest='from_dir',
                        help='''Source folder with unorganized songs''')
    parser.add_argument('--to', default='Music', dest='to_dir',
                        help='''Target folder with organized songs''')
    parser.add_argument('--verbose', action='store_true', dest='verbose',
                        help='''Whether to print all info''')
    args = parser.parse_args()

    if not os.path.isdir(args.to_dir):
        os.mkdir(args.to_dir)
    for f in glob.glob(args.from_dir + "/**", recursive=True):
        if not os.path.isfile(f):
            continue
        song(f, args.to_dir, args.verbose)
    print("Complete!")
