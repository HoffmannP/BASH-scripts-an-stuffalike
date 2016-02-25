#!/bin/bash

fieldModel="Model"
fieldDateTime="Date_and_Time"

model="$(exif -x "$1" | xml_grep --text_only $fieldModel | sed 's/ /_/g')"
dateTime="$(exif -x "$1" | xml_grep --text_only $fieldDateTime | sed 's/[: ]/-/g')"

suffix="$(echo "$1" | rev | cut -d. -f1 | rev)"

ln "$1" "$dateTime:$model.$suffix"

