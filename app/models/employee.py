from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import String, Date, Numeric, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                     default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(150))
    code: Mapped[str | None] = mapped_column(String(20), unique=True)
    manager_id: Mapped[str | None] = mapped_column(ForeignKey("employees.id"))
    management_style: Mapped[str | None] = mapped_column(String(50))

    employees = relationship(
        "Employee",
        back_populates="department",
        foreign_keys="Employee.department_id",
    )


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                     default=lambda: str(uuid4()))
    employee_code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)

    # === NOUVEAU : telephone ===
    phone: Mapped[str | None] = mapped_column(String(20))

    gender: Mapped[str | None] = mapped_column(String(1))

    # === DEJA EN BASE, maintenant declare dans le modele ===
    birth_date: Mapped[date | None]

    job_title: Mapped[str] = mapped_column(String(150))
    department_id: Mapped[str | None] = mapped_column(ForeignKey("departments.id"))
    manager_id: Mapped[str | None] = mapped_column(ForeignKey("employees.id"))
    contract_type: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="actif")
    hire_date: Mapped[date]
    departure_date: Mapped[date | None]
    departure_reason: Mapped[str | None] = mapped_column(String(50))
    city: Mapped[str | None] = mapped_column(String(100))
    work_mode: Mapped[str | None] = mapped_column(String(20))
    remote_days_per_week: Mapped[int] = mapped_column(Integer, default=0)
    salary_base: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    salary_variable: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    disc_profile: Mapped[str | None] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    department = relationship(
        "Department",
        back_populates="employees",
        foreign_keys=[department_id],
    )
    leave_requests = relationship(
        "LeaveRequest",
        back_populates="employee",
        foreign_keys="LeaveRequest.employee_id",
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def seniority_years(self) -> float:
        return round((date.today() - self.hire_date).days / 365.25, 2)

    @property
    def age(self) -> int | None:
        if not self.birth_date:
            return None
        today = date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age