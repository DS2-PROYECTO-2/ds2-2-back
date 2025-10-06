import os
import sys
from pathlib import Path


def main() -> int:
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ds2_back.settings")

    import django  # type: ignore
    django.setup()

    from django.conf import settings  # type: ignore

    db = settings.DATABASES.get("default", {})
    print("Base de datos efectiva (default):")
    print(f"  ENGINE = {db.get('ENGINE')}")
    print(f"  NAME   = {db.get('NAME')}")
    print(f"  HOST   = {db.get('HOST')}")
    print(f"  PORT   = {db.get('PORT')}")
    print(f"  USER   = {db.get('USER')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


