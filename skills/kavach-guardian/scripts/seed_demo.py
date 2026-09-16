"""Seed the demo household (idempotent). Run: python skills/kavach-guardian/scripts/seed_demo.py"""
from agent import models

senior = models.ensure_seed("demo-senior")
print("senior:", senior["name"], "| contacts:", len(models.list_contacts("demo-senior")),
      "| routines:", len(models.list_routines("demo-senior")))
