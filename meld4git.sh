#!/bin/bash

# So ruft git ein externes diff-Programm beim Vergleich von zwei Ordnern/Dateien auf:
# 0. Full name of programm
# 1. git-URI of file 1
# 2. real (temporary) path name of file 1
# 3. SHA1 key of file 1
# 4. fileMode of file 1
# 5. real (temporary) path name of file 2
# 6. SHA1 key of file 2
# 7. fileMode of file 2
# 8. git-URI of file 2 (nur beim Vergleich von Dateien)
# 9. "index f14825f..803cf7a 100644" (nur beim Vergleich von Dateien) <- bin mir nicht sicher was das ist… 

/usr/bin/meld "$2" "$5"