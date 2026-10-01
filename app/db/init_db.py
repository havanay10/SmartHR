from app.db.connection import engine
from app.models.base import Base
import app.models  # noqa — force le chargement de tous les modeles


def create_all():
    """Cree toutes les tables dans la base."""
    Base.metadata.create_all(bind=engine)
    tables = list(Base.metadata.tables.keys())
    print(f"OK - {len(tables)} tables creees :")
    for t in sorted(tables):
        print(f"   - {t}")


def drop_all():
    """Supprime toutes les tables (destructif)."""
    Base.metadata.drop_all(bind=engine)
    print("Toutes les tables supprimees")


if __name__ == "__main__":
    create_all()