#!/bin/bash
pico2wave -w=/tmp/test.wav "This is a test of the Pico Text to Speech"
aplay /tmp/test.wav
rm /tmp/test.wav

