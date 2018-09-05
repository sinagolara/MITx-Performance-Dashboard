#!/bin/bash
cd "${BASH_SOURCE%/*}"
echo "$(date)"
echo "MM Data download started $(date)." | mail -s "MM Data download started $(date)" sina.golara@gmail.com
~/anaconda2/bin/python2.7 main.py
sleep 1
echo "MM Data download complete $(date)." | mail -s "MM Data download complete $(date)" sina.golara@gmail.com
echo "End."
