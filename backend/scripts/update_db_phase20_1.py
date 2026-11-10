import sqlite3

for db_path in ['amit_concierge.db', 'backend/amit_concierge.db']:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    # 1. guest_profiles
    cols = [c[1] for c in cur.execute('PRAGMA table_info(guest_profiles)').fetchall()]
    if 'currency' not in cols:
        cur.execute("ALTER TABLE guest_profiles ADD COLUMN currency VARCHAR(10) DEFAULT 'INR'")
    if 'is_shared_contact' not in cols:
        cur.execute("ALTER TABLE guest_profiles ADD COLUMN is_shared_contact BOOLEAN DEFAULT 0")
    # 2. reservation_modification_requests
    cols = [c[1] for c in cur.execute('PRAGMA table_info(reservation_modification_requests)').fetchall()]
    if 'old_status' not in cols:
        cur.execute("ALTER TABLE reservation_modification_requests ADD COLUMN old_status VARCHAR(30)")
    # 3. notification_logs
    cols = [c[1] for c in cur.execute('PRAGMA table_info(notification_logs)').fetchall()]
    if 'attempts' not in cols:
        cur.execute("ALTER TABLE notification_logs ADD COLUMN attempts INTEGER DEFAULT 1")
    con.commit()
    con.close()
    print("Updated schema for", db_path)
