#!/bin/bash

cat screenlog.0 | grep "has started bot" | cut -d " " -f8 | uniq
