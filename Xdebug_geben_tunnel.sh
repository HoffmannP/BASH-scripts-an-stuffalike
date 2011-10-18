#!/bin/bash
FromHost="sefu";
FromPort="9000";
ToHost="localhost";
ToPort="9000";
echo "currently tunneling $FromHost:$FromPort -> $ToHost:$ToPort"
ssh -c blowfish -NR $FromPort:$ToHost:$ToPort "$FromHost";
