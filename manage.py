"""
(C) 2013-2024 Copycat Software Corporation. All Rights Reserved.

The Copyright Owner has not given any Authority for any Publication of this Work.
This Work contains valuable Trade Secrets of Copycat, and must be maintained in Confidence.
Use of this Work is governed by the Terms and Conditions of a License Agreement with Copycat.

"""

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.local")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
