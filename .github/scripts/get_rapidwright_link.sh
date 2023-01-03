#!/bin/bash

set -e

CURL_RESPONSE="$(curl -s --retry 5 --retry-delay 10 https://api.github.com/repos/Xilinx/RapidWright/releases/latest)"
RAPIDWRIGHT_JAR_LINK="$(echo "$CURL_RESPONSE" | grep "browser_download_url.*_jars.zip" | cut -d : -f 2,3 | tr -d \" | tr -d " ")"

if [ "$RAPIDWRIGHT_JAR_LINK" == "" ]; then
	echo "Error while obtaining RapidWright JAR Link" >&2
	echo "curl response: $CURL_RESPONSE" >&2
	exit 1
fi

echo "link=$RAPIDWRIGHT_JAR_LINK"
