import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import os

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                dbname=st.secrets["DB_NAME"],
                user=st.secrets["DB_USER"],
                password=st.secrets["DB_PASSWORD"],  # Updated password
                host=st.secrets["DB_HOST"],  # Updated host
                port=5432,  # Port remains the same
                sslmode='require'
            )

            self.create_tables()
        except psycopg2.OperationalError:
            # If connection fails, try to create the database
            raise Exception("Failed to connect to database. Please check your credentials.")
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("CREATE DATABASE postgres")
            conn.close()
            # Try connecting again
            self.conn = psycopg2.connect(
                dbname='postgres',
                user='runner',
                password='',
                host='127.0.0.1',
                port=5432,
                options="-c client_encoding=utf8"
            )
            self.create_tables()

    def create_tables(self):
        with self.conn.cursor() as cur:
            # Create tables if they don't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS batches (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS records (
                    id SERIAL PRIMARY KEY,
                    batch_id INTEGER REFERENCES batches(id),
                    file_name VARCHAR(255),
                    ক্রমিক_নং VARCHAR(50),
                    নাম TEXT,
                    ভোটার_নং VARCHAR(100),
                    পিতার_নাম TEXT,
                    মাতার_নাম TEXT,
                    পেশা TEXT,
                    জন্ম_তারিখ VARCHAR(100),
                    ঠিকানা TEXT,
                    phone_number VARCHAR(50),
                    facebook_link TEXT,
                    photo_link TEXT,
                    description TEXT,
                    relationship_status VARCHAR(10) DEFAULT 'Regular',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()
            self.conn.commit()

    def clear_all_data(self):
        """Clear all data from the database"""
        with self.conn.cursor() as cur:
            cur.execute("TRUNCATE records CASCADE")
            cur.execute("TRUNCATE batches CASCADE")
            self.conn.commit()

    def get_batch_files(self, batch_id):
        """Get unique files in a batch"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT DISTINCT file_name
                FROM records
                WHERE batch_id = %s
                ORDER BY file_name
            """, (batch_id,))
            return cur.fetchall()

    def get_file_records(self, batch_id, file_name):
        """Get records for a specific file in a batch"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT r.*, b.name as batch_name
                FROM records r
                JOIN batches b ON r.batch_id = b.id
                WHERE r.batch_id = %s AND r.file_name = %s
                ORDER BY r.created_at DESC
            """, (batch_id, file_name))
            return cur.fetchall()

    def add_batch(self, batch_name):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "INSERT INTO batches (name) VALUES (%s) RETURNING id, name, created_at",
                (batch_name,)
            )
            result = cur.fetchone()
            self.conn.commit()
            return result['id']

    def add_record(self, batch_id, file_name, record_data):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO records (
                    batch_id, file_name, ক্রমিক_নং, নাম, ভোটার_নং,
                    পিতার_নাম, মাতার_নাম, পেশা, জন্ম_তারিখ, ঠিকানা,
                    phone_number, facebook_link, photo_link, description,
                    relationship_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                batch_id, file_name,
                record_data.get('ক্রমিক_নং'), record_data.get('নাম'),
                record_data.get('ভোটার_নং'), record_data.get('পিতার_নাম'),
                record_data.get('মাতার_নাম'), record_data.get('পেশা'),
                record_data.get('জন্ম_তারিখ'), record_data.get('ঠিকানা'),
                record_data.get('phone_number'), record_data.get('facebook_link'),
                record_data.get('photo_link'), record_data.get('description'),
                'Regular'
            ))
            self.conn.commit()

    def update_record(self, record_id, updated_data):
        """Update a record with new data"""
        with self.conn.cursor() as cur:
            query = """
                UPDATE records SET
                    ক্রমিক_নং = %s,
                    নাম = %s,
                    ভোটার_নং = %s,
                    পিতার_নাম = %s,
                    মাতার_নাম = %s,
                    পেশা = %s,
                    ঠিকানা = %s,
                    জন্ম_তারিখ = %s,
                    phone_number = %s,
                    facebook_link = %s,
                    photo_link = %s,
                    description = %s,
                    relationship_status = %s
                WHERE id = %s
            """
            values = (
                str(updated_data.get('ক্রমিক_নং', '')),
                str(updated_data.get('নাম', '')),
                str(updated_data.get('ভোটার_নং', '')),
                str(updated_data.get('পিতার_নাম', '')),
                str(updated_data.get('মাতার_নাম', '')),
                str(updated_data.get('পেশা', '')),
                str(updated_data.get('ঠিকানা', '')),
                str(updated_data.get('জন্ম_তারিখ', '')),
                str(updated_data.get('phone_number', '')),
                str(updated_data.get('facebook_link', '')),
                str(updated_data.get('photo_link', '')),
                str(updated_data.get('description', '')),
                str(updated_data.get('relationship_status', 'Regular')),
                record_id
            )
            cur.execute(query, values)
            self.conn.commit()


    def search_records_advanced(self, criteria):
        """Advanced search with multiple criteria"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT r.*, b.name as batch_name
                FROM records r
                JOIN batches b ON r.batch_id = b.id
                WHERE 1=1
            """
            params = []

            for field, value in criteria.items():
                if value and field != 'relationship_status':
                    query += f" AND {field} ILIKE %s"
                    params.append(f"%{value}%")
                elif value and field == 'relationship_status':
                    query += f" AND {field} = %s"
                    params.append(value)


            query += " ORDER BY r.created_at DESC"
            cur.execute(query, params)
            return cur.fetchall()

    def search_records(self, search_term):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT r.*, b.name as batch_name
                FROM records r
                JOIN batches b ON r.batch_id = b.id
                WHERE 
                    নাম ILIKE %s OR
                    পিতার_নাম ILIKE %s OR
                    মাতার_নাম ILIKE %s OR
                    ঠিকানা ILIKE %s
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            return cur.fetchall()

    def get_all_batches(self):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM batches ORDER BY created_at DESC")
            return cur.fetchall()

    def get_batch_records(self, batch_id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            if batch_id is None:
                cur.execute("""
                    SELECT r.*, b.name as batch_name
                    FROM records r
                    JOIN batches b ON r.batch_id = b.id
                    ORDER BY r.created_at DESC
                """)
            else:
                cur.execute("""
                    SELECT r.*, b.name as batch_name
                    FROM records r
                    JOIN batches b ON r.batch_id = b.id
                    WHERE r.batch_id = %s
                    ORDER BY r.created_at DESC
                """, (batch_id,))
            return cur.fetchall()

    def get_batch_occupation_stats(self, batch_id):
        """Get occupation statistics for a specific batch"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT পেশা, COUNT(*) as count
                FROM records
                WHERE batch_id = %s
                GROUP BY পেশা
                ORDER BY count DESC
            """, (batch_id,))
            return cur.fetchall()

    def get_occupation_stats(self):
        """Get overall occupation statistics"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT পেশা, COUNT(*) as count
                FROM records
                GROUP BY পেশা
                ORDER BY count DESC
            """)
            return cur.fetchall()

    def update_relationship_status(self, record_id: int, status: str):
        """Update relationship status for a record"""
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE records 
                SET relationship_status = %s 
                WHERE id = %s
            """, (status, record_id))
            self.conn.commit()

    def get_relationship_records(self, status: str):
        """Get all records with a specific relationship status"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT r.*, b.name as batch_name
                FROM records r
                JOIN batches b ON r.batch_id = b.id
                WHERE r.relationship_status = %s
                ORDER BY r.created_at DESC
            """, (status,))
            return cur.fetchall()

    def remove_relationship(self, record_id: int):
        """Remove a relationship for a record -- this function is now obsolete"""
        pass #This function is no longer needed.

    def get_relationships(self, relationship_type: str):
        """Get all records with a specific relationship type -- This function is now obsolete"""
        pass #This function is no longer needed.

    def get_batch_by_name(self, batch_name):
        """Get batch information by name"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM batches WHERE name = %s", (batch_name,))
            return cur.fetchone()

    def get_batch_by_id(self, batch_id):
        """Get batch information by ID"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM batches WHERE id = %s", (batch_id,))
            return cur.fetchone()

    def get_file_by_id(self, file_id):
        """Get file information by file ID"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT DISTINCT file_name, batch_id
                FROM records
                WHERE id = %s
            """, (file_id,))
            return cur.fetchone()

    def delete_file(self, batch_id: int, file_name: str):
        """Delete a file and all its associated records from a batch"""
        with self.conn.cursor() as cur:
            try:
                # Start transaction
                cur.execute("BEGIN")

                # Delete all records associated with the file
                cur.execute("""
                    DELETE FROM records 
                    WHERE batch_id = %s AND file_name = %s
                """, (batch_id, file_name))

                # Commit transaction
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                logger.error(f"Error deleting file: {str(e)}")
                raise e

    def delete_batch(self, batch_id: int):
        """Delete a batch and all its associated records"""
        with self.conn.cursor() as cur:
            try:
                # Start transaction
                cur.execute("BEGIN")

                # Delete all records in the batch
                cur.execute("DELETE FROM records WHERE batch_id = %s", (batch_id,))

                # Delete the batch
                cur.execute("DELETE FROM batches WHERE id = %s", (batch_id,))

                # Commit transaction
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                logger.error(f"Error deleting batch: {str(e)}")
                raise e
