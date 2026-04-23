"""
migrate_to_mysql.py
Migrates all data from SQLite to MySQL
Run with: python migrate_to_mysql.py
"""

import sqlite3
import pymysql

SQLITE_DB   = "health_app.db"
MYSQL_HOST  = "localhost"
MYSQL_PORT  = 3306
MYSQL_USER  = "health_user"
MYSQL_PASS  = "970Alpha@123"
MYSQL_DB    = "health_app_db"


def get_sqlite():
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    return conn


def get_mysql():
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=MYSQL_DB,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )


def create_mysql_tables(mysql_conn):
    cursor = mysql_conn.cursor()
    print("Creating MySQL tables...")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        hashed_password VARCHAR(255) NOT NULL,
        role ENUM('admin','doctor','patient',
                  'receptionist','pharmacist') DEFAULT 'patient',
        is_active TINYINT(1) DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS departments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT UNIQUE,
        department_id INT,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        specialization VARCHAR(100),
        license_number VARCHAR(50) UNIQUE NOT NULL,
        phone VARCHAR(20),
        consultation_fee FLOAT DEFAULT 0.0,
        available_days VARCHAR(100),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (department_id) REFERENCES departments(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT UNIQUE,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        date_of_birth DATE NOT NULL,
        gender ENUM('male','female','other'),
        blood_group VARCHAR(5),
        phone VARCHAR(20),
        address TEXT,
        emergency_contact VARCHAR(100),
        emergency_phone VARCHAR(20),
        allergies TEXT,
        insurance_id VARCHAR(50),
        insurance_provider VARCHAR(100),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        patient_id INT NOT NULL,
        doctor_id INT NOT NULL,
        appointment_date DATETIME NOT NULL,
        reason TEXT,
        status ENUM('scheduled','completed',
                    'cancelled','no_show') DEFAULT 'scheduled',
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medical_records (
        id INT AUTO_INCREMENT PRIMARY KEY,
        patient_id INT NOT NULL,
        appointment_id INT,
        diagnosis TEXT NOT NULL,
        symptoms TEXT,
        treatment TEXT,
        notes TEXT,
        follow_up_date DATE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(id),
        FOREIGN KEY (appointment_id) REFERENCES appointments(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prescriptions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        patient_id INT NOT NULL,
        doctor_id INT NOT NULL,
        medical_record_id INT,
        medicine_name VARCHAR(200) NOT NULL,
        dosage VARCHAR(100),
        frequency VARCHAR(100),
        duration_days INT,
        instructions TEXT,
        is_dispensed TINYINT(1) DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(id),
        FOREIGN KEY (medical_record_id)
            REFERENCES medical_records(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lab_reports (
        id INT AUTO_INCREMENT PRIMARY KEY,
        patient_id INT NOT NULL,
        medical_record_id INT,
        test_name VARCHAR(200) NOT NULL,
        test_type VARCHAR(100),
        result TEXT,
        reference_range VARCHAR(200),
        is_abnormal TINYINT(1) DEFAULT 0,
        report_date DATE,
        lab_technician VARCHAR(100),
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(id),
        FOREIGN KEY (medical_record_id)
            REFERENCES medical_records(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INT AUTO_INCREMENT PRIMARY KEY,
        item_name VARCHAR(200) NOT NULL,
        category VARCHAR(100),
        quantity INT DEFAULT 0,
        unit VARCHAR(50),
        unit_price FLOAT DEFAULT 0.0,
        reorder_level INT DEFAULT 10,
        expiry_date DATE,
        supplier VARCHAR(200),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS billing (
        id INT AUTO_INCREMENT PRIMARY KEY,
        patient_id INT NOT NULL,
        appointment_id INT,
        invoice_number VARCHAR(50) UNIQUE NOT NULL,
        consultation_fee FLOAT DEFAULT 0.0,
        medicine_charges FLOAT DEFAULT 0.0,
        lab_charges FLOAT DEFAULT 0.0,
        other_charges FLOAT DEFAULT 0.0,
        discount FLOAT DEFAULT 0.0,
        tax FLOAT DEFAULT 0.0,
        total_amount FLOAT DEFAULT 0.0,
        paid_amount FLOAT DEFAULT 0.0,
        balance_due FLOAT DEFAULT 0.0,
        payment_method VARCHAR(50),
        status ENUM('pending','paid',
                    'partial','cancelled') DEFAULT 'pending',
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(id),
        FOREIGN KEY (appointment_id) REFERENCES appointments(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS billing_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        bill_id INT NOT NULL,
        inventory_id INT,
        description VARCHAR(200) NOT NULL,
        quantity INT DEFAULT 1,
        unit_price FLOAT DEFAULT 0.0,
        total_price FLOAT DEFAULT 0.0,
        FOREIGN KEY (bill_id) REFERENCES billing(id),
        FOREIGN KEY (inventory_id) REFERENCES inventory(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    mysql_conn.commit()
    print("  All tables created successfully")


def migrate_table(sqlite_conn, mysql_conn,
                  table, insert_sql, transform=None):
    sc = sqlite_conn.cursor()
    mc = mysql_conn.cursor()

    sc.execute(f"SELECT * FROM {table}")
    rows = sc.fetchall()

    if not rows:
        print(f"  {table} — no data found")
        return 0

    count = 0
    for row in rows:
        data = dict(row)
        if transform:
            data = transform(data)
        try:
            mc.execute(insert_sql, data)
            count += 1
        except pymysql.err.IntegrityError:
            pass

    mysql_conn.commit()
    print(f"  {table} — {count} rows migrated successfully")
    return count


def run_migration():
    print("")
    print("Starting Migration: SQLite to MySQL")
    print("=" * 45)

    try:
        sqlite_conn = get_sqlite()
        print("  SQLite connected")
    except Exception as e:
        print(f"  SQLite error: {e}")
        return

    try:
        mysql_conn = get_mysql()
        print("  MySQL connected")
    except Exception as e:
        print(f"  MySQL connection failed: {e}")
        print("")
        print("  Please check:")
        print("  1. MySQL is running")
        print("  2. Database health_app_db exists")
        print("  3. Username: health_user")
        print("  4. Password: Health@1234")
        return

    print("")
    create_mysql_tables(mysql_conn)

    print("")
    print("Migrating data...")
    print("")

    migrate_table(
        sqlite_conn, mysql_conn, "users",
        """INSERT IGNORE INTO users
           (id, username, email, hashed_password,
            role, is_active, created_at)
           VALUES (%(id)s, %(username)s, %(email)s,
                   %(hashed_password)s, %(role)s,
                   %(is_active)s, %(created_at)s)"""
    )

    migrate_table(
        sqlite_conn, mysql_conn, "departments",
        """INSERT IGNORE INTO departments
           (id, name, description, created_at)
           VALUES (%(id)s, %(name)s,
                   %(description)s, %(created_at)s)"""
    )

    migrate_table(
        sqlite_conn, mysql_conn, "doctors",
        """INSERT IGNORE INTO doctors
           (id, user_id, department_id, first_name,
            last_name, specialization, license_number,
            phone, consultation_fee, available_days,
            created_at)
           VALUES (%(id)s, %(user_id)s, %(department_id)s,
                   %(first_name)s, %(last_name)s,
                   %(specialization)s, %(license_number)s,
                   %(phone)s, %(consultation_fee)s,
                   %(available_days)s, %(created_at)s)"""
    )

    migrate_table(
        sqlite_conn, mysql_conn, "patients",
        """INSERT IGNORE INTO patients
           (id, user_id, first_name, last_name,
            date_of_birth, gender, blood_group,
            phone, address, emergency_contact,
            emergency_phone, allergies,
            insurance_id, insurance_provider, created_at)
           VALUES (%(id)s, %(user_id)s, %(first_name)s,
                   %(last_name)s, %(date_of_birth)s,
                   %(gender)s, %(blood_group)s, %(phone)s,
                   %(address)s, %(emergency_contact)s,
                   %(emergency_phone)s, %(allergies)s,
                   %(insurance_id)s, %(insurance_provider)s,
                   %(created_at)s)"""
    )

    migrate_table(
        sqlite_conn, mysql_conn, "appointments",
        """INSERT IGNORE INTO appointments
           (id, patient_id, doctor_id,
            appointment_date, reason,
            status, notes, created_at)
           VALUES (%(id)s, %(patient_id)s, %(doctor_id)s,
                   %(appointment_date)s, %(reason)s,
                   %(status)s, %(notes)s, %(created_at)s)"""
    )

    migrate_table(
        sqlite_conn, mysql_conn, "medical_records",
        """INSERT IGNORE INTO medical_records
           (id, patient_id, appointment_id,
            diagnosis, symptoms, treatment,
            notes, follow_up_date, created_at)
           VALUES (%(id)s, %(patient_id)s,
                   %(appointment_id)s, %(diagnosis)s,
                   %(symptoms)s, %(treatment)s,
                   %(notes)s, %(follow_up_date)s,
                   %(created_at)s)"""
    )

    migrate_table(
        sqlite_conn, mysql_conn, "prescriptions",
        """INSERT IGNORE INTO prescriptions
           (id, patient_id, doctor_id,
            medical_record_id, medicine_name,
            dosage, frequency, duration_days,
            instructions, is_dispensed, created_at)
           VALUES (%(id)s, %(patient_id)s, %(doctor_id)s,
                   %(medical_record_id)s, %(medicine_name)s,
                   %(dosage)s, %(frequency)s,
                   %(duration_days)s, %(instructions)s,
                   %(is_dispensed)s, %(created_at)s)"""
    )

    migrate_table(
        sqlite_conn, mysql_conn, "lab_reports",
        """INSERT IGNORE INTO lab_reports
           (id, patient_id, medical_record_id,
            test_name, test_type, result,
            reference_range, is_abnormal,
            report_date, lab_technician,
            notes, created_at)
           VALUES (%(id)s, %(patient_id)s,
                   %(medical_record_id)s, %(test_name)s,
                   %(test_type)s, %(result)s,
                   %(reference_range)s, %(is_abnormal)s,
                   %(report_date)s, %(lab_technician)s,
                   %(notes)s, %(created_at)s)"""
    )

    migrate_table(
        sqlite_conn, mysql_conn, "inventory",
        """INSERT IGNORE INTO inventory
           (id, item_name, category, quantity,
            unit, unit_price, reorder_level,
            expiry_date, supplier, created_at)
           VALUES (%(id)s, %(item_name)s, %(category)s,
                   %(quantity)s, %(unit)s, %(unit_price)s,
                   %(reorder_level)s, %(expiry_date)s,
                   %(supplier)s, %(created_at)s)"""
    )

    migrate_table(
        sqlite_conn, mysql_conn, "billing",
        """INSERT IGNORE INTO billing
           (id, patient_id, appointment_id,
            invoice_number, consultation_fee,
            medicine_charges, lab_charges,
            other_charges, discount, tax,
            total_amount, paid_amount,
            balance_due, payment_method,
            status, notes, created_at)
           VALUES (%(id)s, %(patient_id)s,
                   %(appointment_id)s, %(invoice_number)s,
                   %(consultation_fee)s, %(medicine_charges)s,
                   %(lab_charges)s, %(other_charges)s,
                   %(discount)s, %(tax)s, %(total_amount)s,
                   %(paid_amount)s, %(balance_due)s,
                   %(payment_method)s, %(status)s,
                   %(notes)s, %(created_at)s)"""
    )

    migrate_table(
        sqlite_conn, mysql_conn, "billing_items",
        """INSERT IGNORE INTO billing_items
           (id, bill_id, inventory_id,
            description, quantity,
            unit_price, total_price)
           VALUES (%(id)s, %(bill_id)s,
                   %(inventory_id)s, %(description)s,
                   %(quantity)s, %(unit_price)s,
                   %(total_price)s)"""
    )

    sqlite_conn.close()
    mysql_conn.close()

    print("")
    print("=" * 45)
    print("Migration completed successfully!")
    print("")
    print("MySQL Connection Details:")
    print(f"  Host:     {MYSQL_HOST}")
    print(f"  Port:     {MYSQL_PORT}")
    print(f"  Database: {MYSQL_DB}")
    print(f"  Username: {MYSQL_USER}")
    print(f"  Password: {MYSQL_PASS}")
    print("")
    print("Next step: restart your server")
    print("python -m uvicorn main:app --reload")


if __name__ == "__main__":
    run_migration()