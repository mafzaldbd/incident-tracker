import random
from datetime import datetime, timezone
from app.database import SessionLocal
from app import models

def check_server_health(server: models.Server) -> tuple[str, bool]:
    """
    Simulates a health check. Returns (status, is_healthy).
    In a real system, this would ping the server, hit a /health endpoint, check CPU via an agent, etc.
    """
    cpu_usage = random.randint(0, 100)
    if cpu_usage > 85:
        return "critical", False
    elif cpu_usage > 70:
        return "warning", False
    return "healthy", True


def run_health_check():
    db = SessionLocal()
    try:
        servers = db.query(models.Server).all()
        print(f"[{datetime.now()}] Checking {len(servers)} server(s)...")

        for server in servers:
            status, is_healthy = check_server_health(server)

            server.status = status
            server.last_checked = datetime.now(timezone.utc)

            if not is_healthy:
                incident = models.Incident(
                    server_id=server.id,
                    title=f"Auto-detected: {server.name} health check failed",
                    description=f"Simulated health check returned status '{status}'.",
                    severity="high" if status == "critical" else "medium",
                    status="open",
                )
                db.add(incident)
                print(f"  -> Incident auto-created for {server.name} ({status})")
            else:
                print(f"  -> {server.name} healthy")

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run_health_check()