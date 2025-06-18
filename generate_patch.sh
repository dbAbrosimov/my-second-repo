#!/bin/bash
# Save diff of staged changes to update.patch in unified format

git diff --cached -u > update.patch
printf 'Patch saved to update.patch\n'
