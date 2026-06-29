from pydantic import BaseModel


class DashboardSummary(BaseModel):
    online: int
    offline: int
    alerts: int
    towers: int
    generators: int
    tanks: int
    sensors: int
