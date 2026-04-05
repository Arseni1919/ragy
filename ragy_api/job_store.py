import sqlite3
from datetime import datetime
from typing import Optional


class JobMetadataStore:
    def __init__(self, db_path: str = "./ragy_jobs.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                apscheduler_job_id TEXT NOT NULL UNIQUE,
                query TEXT NOT NULL,
                collection_name TEXT NOT NULL,
                interval_type TEXT NOT NULL,
                interval_amount INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_run TIMESTAMP NULL,
                last_success TIMESTAMP NULL,
                run_count INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                last_error TEXT NULL
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_apscheduler_job_id ON job_metadata(apscheduler_job_id)')
        conn.commit()
        conn.close()

    def create_job(self, query: str, collection_name: str, interval_type: str, interval_amount: int) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO job_metadata (query, collection_name, interval_type, interval_amount, apscheduler_job_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (query, collection_name, interval_type, interval_amount, ''))
        job_id = cursor.lastrowid
        apscheduler_job_id = f"user_job_{job_id}"
        cursor.execute('UPDATE job_metadata SET apscheduler_job_id = ? WHERE id = ?', (apscheduler_job_id, job_id))
        conn.commit()
        conn.close()
        return job_id

    def get_job(self, job_id: int) -> Optional[dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM job_metadata WHERE id = ?', (job_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            'id': row[0],
            'apscheduler_job_id': row[1],
            'query': row[2],
            'collection_name': row[3],
            'interval_type': row[4],
            'interval_amount': row[5],
            'created_at': row[6],
            'last_run': row[7],
            'last_success': row[8],
            'run_count': row[9],
            'error_count': row[10],
            'last_error': row[11]
        }

    def list_jobs(self) -> list[dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM job_metadata ORDER BY id')
        rows = cursor.fetchall()
        conn.close()

        jobs = []
        for row in rows:
            jobs.append({
                'id': row[0],
                'apscheduler_job_id': row[1],
                'query': row[2],
                'collection_name': row[3],
                'interval_type': row[4],
                'interval_amount': row[5],
                'created_at': row[6],
                'last_run': row[7],
                'last_success': row[8],
                'run_count': row[9],
                'error_count': row[10],
                'last_error': row[11]
            })
        return jobs

    def delete_job(self, job_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM job_metadata WHERE id = ?', (job_id,))

        cursor.execute('SELECT COUNT(*) FROM job_metadata')
        remaining_jobs = cursor.fetchone()[0]

        if remaining_jobs == 0:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='job_metadata'")

        conn.commit()
        conn.close()

    def update_run_stats(self, job_id: int, success: bool, error: Optional[str] = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        if success:
            cursor.execute('''
                UPDATE job_metadata
                SET last_run = ?, last_success = ?, run_count = run_count + 1, last_error = NULL
                WHERE id = ?
            ''', (now, now, job_id))
        else:
            cursor.execute('''
                UPDATE job_metadata
                SET last_run = ?, error_count = error_count + 1, run_count = run_count + 1, last_error = ?
                WHERE id = ?
            ''', (now, error, job_id))

        conn.commit()
        conn.close()
