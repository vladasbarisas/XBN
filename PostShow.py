#!/usr/bin/python3

"""PostShow v1.2 (https://github.com/vladasbarisas/XBN)

Python script to generate JSON MP3 chapters, LRC, CUE and simple timestamp files from an Audacity label file.
Written by Manual (@CatVsHumanity on Twitter)
"""

import csv
import os
import sys
import time
import argparse


def main(args):
    if not os.path.isfile(args.input):
        sys.exit("File does not exist. Aborting.")

    reader = csv.reader(open(args.input, encoding="utf-8"), delimiter='	', quoting=csv.QUOTE_NONE)
    json_output = open(os.path.join(args.output, args.title) + '.json', 'w', encoding="utf-8")
    cue_output = open(os.path.join(args.output, args.title) + '.cue', 'w', encoding="utf-8")
    lrc_output = open(os.path.join(args.output, args.title) + '.lrc', 'w', encoding="utf-8")
    simple_output = open(os.path.join(args.output, args.title) + '-simple.txt', 'w', encoding="utf-8")
    trackno = 1
    cue_initialized = False  # write CUE header before loop starts
    lrc_initialized = False  # write LRC header before loop starts
    cue_output.write('\ufeff')  # encode CUE file as UTF-8 BOM for compatibility with foobar2000
    bit = []
    json_bit = []

    for row in reader:
        if not row:
            break  # Reached EOF

        # Math
        math_milliseconds_total = format(float(row[0]) * 1000, '.1f')
        math_minutes_total = int(time.strftime('%H', time.gmtime(int(float(row[0]))))) * 60 + int(time.strftime('%M', time.gmtime(int(float(row[0])))))
        math_seconds = int(time.strftime('%S', time.gmtime(int(float(row[0])))))
        math_centiseconds = format(float(row[0]) % 1, '.2f')[2:]

        # JSON
        bit.append(row[2].replace('"', '\u201d'))
        bit.append(float(math_milliseconds_total))
        json_bit.append(bit)
        bit = []

        # LRC
        if lrc_initialized is not True:
            lrc_output.write('[ti:{}]\n'.format(args.title))
            lrc_output.write('[ar:{}]\n'.format("..::XANA Creations::.."))
            lrc_output.write('[al:{}]\n'.format("The Friday Night Tech Podcast"))
            lrc_initialized = True
        lrc_output.write('[' + str(math_minutes_total).zfill(2) + ':' + str(math_seconds).zfill(2) + '.' + str(math_centiseconds).zfill(2) + ']' + row[2] + '\n')

        # CUE
        if cue_initialized is not True:
            cue_output.write('REM GENRE Podcast\n')
            cue_output.write('REM COMMENT "This cue file has been generated by PostShow v2 (https://github.com/vladasbarisas/XBN)"\n')
            cue_output.write('TITLE "' + args.title + '"\n')
            cue_output.write('PERFORMER "' + "XBN" + '"\n')
            cue_output.write('FILE "' + args.filename + '" MP3\n')
            cue_initialized = True
        cue_output.write('  TRACK ' + str(trackno).zfill(2) + ' AUDIO\n')
        cue_output.write('    TITLE "' + row[2].replace('"', '\u201d') + '"\n')
        cue_output.write('    INDEX 01 ' + str(math_minutes_total).zfill(2) + ':' + str(math_seconds).zfill(2) + ':' + str(math_centiseconds).zfill(2) + '\n')
        trackno += 1

        # Simple
        simple_output.write(time.strftime('%H:%M:%S', time.gmtime(int(float(row[0])))) + ' - ' + row[2] + '\n')

    # Fix up JSON after the loop is done
    json_output.write(str(json_bit).replace("['", '["').replace("', ", '", '))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate CUE, LRC, JSON and timestamp files from an Audacity label file')
    parser.add_argument("input", help="path to audacity file")
    parser.add_argument("output", help="output directory (with a leading slash!)")
    parser.add_argument("title", help="episode title")
    parser.add_argument("filename", help="episode file name (for example fnt-200.mp3)")
    arguments = parser.parse_args()

    main(arguments)
