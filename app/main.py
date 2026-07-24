from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from apscheduler.schedulers.background import BackgroundScheduler
from app.routers import servers, incidents, incidents_logs
from monitor import run_health_check

app = FastAPI(title="Incident Tracker")

app.include_router(servers.router)
app.include_router(incidents.router)
app.include_router(incidents_logs.router)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/dashboard")
def dashboard():
    return FileResponse("static/dashboard.html")


scheduler = BackgroundScheduler()


@app.on_event("startup")
def start_scheduler():
    scheduler.add_job(run_health_check, "interval", minutes=15)
    scheduler.start()
    print("Scheduler started — health checks every 15 minutes.")


@app.on_event("shutdown")
def stop_scheduler():
    scheduler.shutdown()


@app.get("/")
def health_check():
    return {"status": "ok"}
