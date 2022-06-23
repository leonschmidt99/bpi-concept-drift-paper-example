#!/usr/bin/env python3
from string import ascii_uppercase

ACTIVITIES = [
    "find out position requirements",
    "create job posting",
    "check formal requirements",
    "reject application",
    "invite to pre-screening",
    "perform pre-screening via telephone",
    "perform pre-screening via video call",
    "assess initial performance",
    "invite to basic live interviews",
    "perform assessment interview",
    "perform coding interview",
    "assess midway performance",
    "invite to advanced live interviews",
    "perform manager interview",
    "perform architecture/design interview",
    "assess final performance",
    "send offer",
    "negotiate salary",
]

LETTERS = ascii_uppercase[:len(ACTIVITIES)]
# LETTERS = "abcdefghijk"  # for testing wrt the paper
