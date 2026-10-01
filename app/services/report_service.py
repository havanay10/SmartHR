from datetime import datetime
from uuid import uuid4
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy import select, func
from app.db.connection import get_session
from app.models.report import Report
from app.models.employee import Employee, Department
from config import settings

REPORT_TYPES = {
    "remuneration_by_dept": "Analyse des remunerations par departement",
    "turnover_absenteeism": "Analyse du turnover et de l'absenteisme",
    "age_pyramid": "Pyramide des ages et de l'anciennete",
    "salary_projection": "Projection de la masse salariale",
}


class ReportService:
    """Service de generation de rapports PDF (CDC §6)."""

    def generate(self, report_type: str) -> str:
        if report_type not in REPORT_TYPES:
            raise ValueError(f"Type invalide : {report_type}")

        title = REPORT_TYPES[report_type]
        filename = f"{report_type}_{datetime.now():%Y%m%d_%H%M%S}.pdf"
        path = settings.EXPORT_DIR / filename

        c = canvas.Canvas(str(path), pagesize=A4)
        width, height = A4
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 60, f"SmartRH - {title}")
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 80, f"Genere le {datetime.now():%d/%m/%Y %H:%M}")

        y = height - 120
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Donnees :")
        y -= 20

        with get_session() as db:
            if report_type == "remuneration_by_dept":
                stmt = (
                    select(
                        Department.name,
                        func.avg(Employee.salary_base),
                        func.count(Employee.id),
                    )
                    .join(Employee, Employee.department_id == Department.id)
                    .group_by(Department.name)
                )
                c.setFont("Helvetica", 10)
                for row in db.execute(stmt):
                    c.drawString(
                        50, y,
                        f"{row[0]} - moyenne : {float(row[1] or 0):,.0f} EUR ({row[2]} pers.)"
                    )
                    y -= 15

            elif report_type == "turnover_absenteeism":
                total = db.scalar(select(func.count()).select_from(Employee)) or 0
                left = db.scalar(
                    select(func.count()).select_from(Employee)
                    .where(Employee.departure_date.isnot(None))
                ) or 0
                rate = round(100 * left / max(total, 1), 2)
                c.setFont("Helvetica", 10)
                c.drawString(50, y, f"Turnover annuel : {rate}%")
                y -= 15
                c.drawString(50, y, f"Effectif total : {total}")
                y -= 15

            elif report_type == "age_pyramid":
                emps = db.scalars(select(Employee)).all()
                tranches = {"<30": 0, "30-40": 0, "40-50": 0, "50+": 0}
                for e in emps:
                    age = (datetime.now().date() - e.hire_date).days // 365
                    if age < 30:
                        tranches["<30"] += 1
                    elif age < 40:
                        tranches["30-40"] += 1
                    elif age < 50:
                        tranches["40-50"] += 1
                    else:
                        tranches["50+"] += 1
                c.setFont("Helvetica", 10)
                for k, v in tranches.items():
                    c.drawString(50, y, f"{k} ans : {v} employes")
                    y -= 15

            elif report_type == "salary_projection":
                total = db.scalar(
                    select(func.sum(Employee.salary_base))
                    .where(Employee.status == "actif")
                ) or 0
                c.setFont("Helvetica", 10)
                c.drawString(50, y, f"Masse salariale actuelle : {float(total):,.0f} EUR")
                y -= 15
                c.drawString(
                    50, y,
                    f"Projection N+1 (+2.8%) : {float(total) * 1.028:,.0f} EUR"
                )
                y -= 15

        c.save()

        size_kb = path.stat().st_size // 1024
        with get_session() as db:
            db.add(Report(
                id=str(uuid4()),
                report_type=report_type,
                title=title,
                file_url=str(path),
                file_format="PDF",
                file_size_kb=size_kb,
                status="pret",
                created_at=datetime.utcnow(),
            ))
        return str(path)

    def get_latest(self, limit: int = 6) -> list[dict]:
        """Retourne les derniers rapports avec TOUS les champs utiles."""
        with get_session() as db:
            rows = db.scalars(
                select(Report).order_by(Report.created_at.desc()).limit(limit)
            ).all()
            return [
                {
                    "id": r.id,
                    "report_type": r.report_type,
                    "title": r.title,
                    "file_url": r.file_url,          # ⭐ AJOUT
                    "format": r.file_format,
                    "size_kb": r.file_size_kb,
                    "status": r.status,               # ⭐ AJOUT
                    "created_at": r.created_at,
                }
                for r in rows
            ]