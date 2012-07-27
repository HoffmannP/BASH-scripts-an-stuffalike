#!/bin/bash

# So ruft svn ein externes diff-Programm beim Vergleich von zwei Ordnern/Dateien auf:
# 0. Full name of programm
# 1. '-u' Output 3 lines of unified context.
# 2. '-L'
# 3. description of file 1
# 4. '-L'
# 5. description of file 1
# 6. svn URI of file 1
# 7. svn URI of file 2

/usr/bin/meld "$6" "$7"