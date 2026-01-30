
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json
from datetime import datetime

# Add parent dir to path
sys.path.append(os.getcwd())

from app.database import Base
from app.models import VideoJob, JobStatus

# Setup DB connection
DATABASE_URL = "sqlite:///./data/video_reup.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_jobs():
    db = SessionLocal()
    try:
        print(f"Checking jobs at {datetime.now()}...")
        jobs = db.query(VideoJob).order_by(VideoJob.created_at.desc()).limit(10).all()
        
        if not jobs:
            print("No jobs found in database.")
            return

        print(f"{'ID':<38} | {'Status':<12} | {'Created':<20} | {'Step':<30} | {'Error'}")
        print("-" * 120)
        
        for job in jobs:
            status = job.status.value if hasattr(job.status, "value") else job.status
            created = job.created_at.strftime("%Y-%m-%d %H:%M:%S") if job.created_at else "N/A"
            step = (job.current_step or "")[:30]
            error = (job.error_message or "")[:50].replace("\n", " ")
            
            print(f"{job.id:<38} | {status:<12} | {created:<20} | {step:<30} | {error}")
            
            # Print detailed analysis state if stuck
            if status in ["processing", "analyzing", "pending"]:
                print(f"  > Details for {job.id}:")
                if job.analysis_result:
                    ar = job.analysis_result
                    print(f"    Current Stage: {ar.get('current_stage')}")
                    print(f"    Progress: {ar.get('progress')}%")
                else:
                    print("    No analysis_result JSON found.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_jobs()
