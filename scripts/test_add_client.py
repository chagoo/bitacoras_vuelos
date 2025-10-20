from __future__ import annotations

from app.db import get_session
from app.repository import init_db, list_clients, add_client


def main():
    init_db()
    with get_session() as s:
        before = list_clients(s)
        print(f"Clientes antes: {len(before)} -> {[c.name for c in before]}")
        try:
            c = add_client(s, name="VIP EMPRESARIAL")
            print(f"Agregado id={c.id} name={c.name}")
        except Exception as e:
            print("ERROR al agregar:", e)
    with get_session() as s:
        after = list_clients(s)
        print(f"Clientes después: {len(after)} -> {[c.name for c in after]}")


if __name__ == "__main__":
    main()
