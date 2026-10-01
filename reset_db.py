"""Reset complet de la base de donnees.

Supprime TOUTES les tables avec CASCADE (PostgreSQL natif),
puis recree le schema.
"""
from sqlalchemy import text
from app.db.connection import engine
from app.db.init_db import create_all


def reset_database():
    print("Suppression de toutes les tables...")
    with engine.begin() as conn:
        # Supprimer le schema public entier (CASCADE)
        conn.execute(text("DROP SCHEMA public CASCADE"))
        # Recreer le schema
        conn.execute(text("CREATE SCHEMA public"))
        # Donner les droits
        conn.execute(text("GRANT ALL ON SCHEMA public TO smartrh"))
        conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
    print("[OK] Schema public reinitialise")

    print("\nCreation des tables...")
    create_all()


if __name__ == "__main__":
    reset_database()