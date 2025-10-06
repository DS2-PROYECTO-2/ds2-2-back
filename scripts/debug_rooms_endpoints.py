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

    from django.contrib.auth import get_user_model  # type: ignore
    from rest_framework.test import APIRequestFactory, force_authenticate  # type: ignore
    from rooms.views import user_room_entries_view, user_active_entry_view  # type: ignore
    from rooms.models import Room, RoomEntry  # type: ignore

    User = get_user_model()

    # Crear usuario verificado si no existe
    user, _ = User.objects.get_or_create(
        username="debug_user",
        defaults={
            "email": "debug@example.com",
            "first_name": "Debug",
            "last_name": "User",
            "role": "monitor",
            "is_active": True,
            "is_verified": True,
        },
    )
    if not user.is_verified:
        user.is_verified = True
        user.is_active = True
        user.save()

    # Crear sala y una entrada activa para probar
    room, _ = Room.objects.get_or_create(code="D1", defaults={"name": "Debug Room", "capacity": 10})
    RoomEntry.objects.filter(user=user, exit_time__isnull=True).update(exit_time=None)
    if not RoomEntry.objects.filter(user=user, exit_time__isnull=True).exists():
        RoomEntry.objects.create(user=user, room=room, notes="debug")

    factory = APIRequestFactory()

    # Probar my-entries
    request1 = factory.get("/api/rooms/my-entries/")
    force_authenticate(request1, user=user)
    resp1 = user_room_entries_view(request1)
    print("my-entries status:", resp1.status_code)
    print("my-entries data keys:", list(getattr(resp1, 'data', {}).keys()) if hasattr(resp1, 'data') else type(resp1))

    # Probar my-active-entry
    request2 = factory.get("/api/rooms/my-active-entry/")
    force_authenticate(request2, user=user)
    resp2 = user_active_entry_view(request2)
    print("my-active-entry status:", resp2.status_code)
    if hasattr(resp2, 'data'):
        print("my-active-entry keys:", list(resp2.data.keys()))
    else:
        print(type(resp2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


