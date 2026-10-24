#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mayan Language & Epigraphy Engine Wrapper (Ah Ts'ib)
Provides standard Python module importing (`import mayan_lang`) for `mayan-lang.py`.
"""
import sys
import importlib

_mod = importlib.import_module("mayan-lang")
for _k, _v in _mod.__dict__.items():
    if not _k.startswith("__"):
        globals()[_k] = _v

if __name__ == "__main__":
    _mod.launch_gui()
