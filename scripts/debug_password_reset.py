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

    from users.models import User  # type: ignore
    from users.serializers import PasswordResetRequestSerializer  # type: ignore

    qs = User.objects.filter(is_active=True).order_by("id")[:5]
    print("Usuarios activos encontrados:")
    for u in qs:
        print("-", u.id, u.username, u.email, "verificado=", u.is_verified)

    if qs:
        email = qs[0].email
        print("\nProbando reset para:", email)
        s = PasswordResetRequestSerializer(data={"email": email})
        if s.is_valid():
            try:
                res = s.save()
                print("Resultado serializer:", res)
            except Exception as e:
                print("ERROR al enviar:", e)
        else:
            print("Errores de validación:", s.errors)
    else:
        print("No hay usuarios activos con email. Crea uno y vuelve a intentar.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


