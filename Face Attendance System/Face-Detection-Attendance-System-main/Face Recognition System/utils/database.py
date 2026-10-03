"""
Database Management Module
Handles all SQLite database operations for the Face Recognition System
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from config import DATABASE_FILE
from utils.constants import (
    COL_USER_ID, COL_USER_NAME, COL_USER_STUDENT_ID, COL_USER_IMAGE_PATH, COL_USER_CREATED_AT,
    COL_USER_EMAIL, COL_USER_PHONE,
    COL_ATTENDANCE_ID, COL_ATTENDANCE_STUDENT_ID, COL_ATTENDANCE_NAME, COL_ATTENDANCE_DATE,
    COL_ATTENDANCE_TIME, COL_ATTENDANCE_STATUS, COL_ATTENDANCE_CONFIDENCE,
    DATETIME_FORMAT
)

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages all database operations for the Face Recognition System.
    """
    
    def __init__(self, db_file=DATABASE_FILE):
        """
        Initialize database manager.
        
        Args:
            db_file (Path): Path to SQLite database file
        """
        self.db_file = Path(db_file)
        self.initialize_database()
    
    def get_connection(self):
        """
        Get database connection.
        
        Returns:
            sqlite3.Connection: Database connection
        """
        try:
            self.db_file.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(self.db_file))
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def initialize_database(self):
        """
        Create database tables if they don't exist.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    student_id TEXT UNIQUE NOT NULL,
                    image_path TEXT,
                    email TEXT,
                    phone TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create Attendance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    date DATE NOT NULL,
                    time TIME NOT NULL,
                    status TEXT DEFAULT 'Present',
                    confidence REAL DEFAULT 0.0,
                    FOREIGN KEY (student_id) REFERENCES users (student_id),
                    UNIQUE(student_id, date)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    # ================== USER MANAGEMENT ==================
    def add_user(self, name, student_id, email=None, phone=None):
        """
        Add a new user to the database.
        
        Args:
            name (str): User's name
            student_id (str): Unique student ID
            email (str): User's email (optional)
            phone (str): User's phone (optional)
            
        Returns:
            int: User ID if successful, None otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (name, student_id, email, phone)
                VALUES (?, ?, ?, ?)
            ''', (name, student_id, email, phone))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"User added: {name} ({student_id})")
            return user_id
        except sqlite3.IntegrityError:
            logger.warning(f"Duplicate student ID: {student_id}")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error adding user: {e}")
            return None
    
    def get_user_by_student_id(self, student_id):
        """
        Get user information by student ID.
        
        Args:
            student_id (str): Student ID
            
        Returns:
            dict: User information or None if not found
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE student_id = ?', (student_id,))
            user = cursor.fetchone()
            conn.close()
            
            return dict(user) if user else None
        except sqlite3.Error as e:
            logger.error(f"Error fetching user: {e}")
            return None
    
    def get_all_users(self):
        """
        Get all users from database.
        
        Returns:
            list: List of user dictionaries
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users ORDER BY name')
            users = cursor.fetchall()
            conn.close()
            
            return [dict(user) for user in users]
        except sqlite3.Error as e:
            logger.error(f"Error fetching users: {e}")
            return []
    
    def update_user(self, student_id, **kwargs):
        """
        Update user information.
        
        Args:
            student_id (str): Student ID
            **kwargs: Fields to update (name, email, phone, image_path)
            
        Returns:
            bool: True if updated, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            allowed_fields = {'name', 'email', 'phone', 'image_path'}
            fields_to_update = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            if not fields_to_update:
                return False
            
            set_clause = ', '.join([f'{field} = ?' for field in fields_to_update.keys()])
            values = list(fields_to_update.values()) + [student_id]
            
            cursor.execute(f'''
                UPDATE users
                SET {set_clause}
                WHERE student_id = ?
            ''', values)
            
            conn.commit()
            conn.close()
            
            logger.info(f"User updated: {student_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating user: {e}")
            return False
    
    def delete_user(self, student_id):
        """
        Delete a user from database.
        
        Args:
            student_id (str): Student ID
            
        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Delete user attendance records first
            cursor.execute('DELETE FROM attendance WHERE student_id = ?', (student_id,))
            
            # Delete user
            cursor.execute('DELETE FROM users WHERE student_id = ?', (student_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"User deleted: {student_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error deleting user: {e}")
            return False
    
    def user_exists(self, student_id):
        """
        Check if user exists.
        
        Args:
            student_id (str): Student ID
            
        Returns:
            bool: True if exists, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT 1 FROM users WHERE student_id = ?', (student_id,))
            exists = cursor.fetchone() is not None
            conn.close()
            
            return exists
        except sqlite3.Error as e:
            logger.error(f"Error checking user existence: {e}")
            return False
    
    # ================== ATTENDANCE MANAGEMENT ==================
    def mark_attendance(self, student_id, name, status="Present", confidence=0.0):
        """
        Mark attendance for a user.
        
        Args:
            student_id (str): Student ID
            name (str): User name
            status (str): Attendance status (Present/Absent/Late)
            confidence (float): Face recognition confidence score
            
        Returns:
            bool: True if marked, False if duplicate
        """
        try:
            from utils.utils import get_current_date, get_current_time
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            today = get_current_date()
            current_time = get_current_time()
            
            # Check if already marked today
            cursor.execute('''
                SELECT id FROM attendance
                WHERE student_id = ? AND date = ?
            ''', (student_id, today))
            
            if cursor.fetchone():
                conn.close()
                logger.warning(f"Duplicate attendance marking: {student_id} on {today}")
                return False
            
            # Mark attendance
            cursor.execute('''
                INSERT INTO attendance (student_id, name, date, time, status, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_id, name, today, current_time, status, confidence))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Attendance marked: {name} ({student_id}) - {status}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error marking attendance: {e}")
            return False
    
    def get_today_attendance(self):
        """
        Get today's attendance records.
        
        Returns:
            list: List of attendance records
        """
        try:
            from utils.utils import get_current_date
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            today = get_current_date()
            cursor.execute('''
                SELECT * FROM attendance
                WHERE date = ?
                ORDER BY time
            ''', (today,))
            
            records = cursor.fetchall()
            conn.close()
            
            return [dict(record) for record in records]
        except sqlite3.Error as e:
            logger.error(f"Error fetching today's attendance: {e}")
            return []
    
    def get_attendance_by_date_range(self, start_date, end_date):
        """
        Get attendance records for a date range.
        
        Args:
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
            
        Returns:
            list: List of attendance records
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM attendance
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC, time DESC
            ''', (start_date, end_date))
            
            records = cursor.fetchall()
            conn.close()
            
            return [dict(record) for record in records]
        except sqlite3.Error as e:
            logger.error(f"Error fetching attendance records: {e}")
            return []
    
    def get_attendance_by_student(self, student_id, start_date=None, end_date=None):
        """
        Get attendance records for a specific student.
        
        Args:
            student_id (str): Student ID
            start_date (str): Start date (optional)
            end_date (str): End date (optional)
            
        Returns:
            list: List of attendance records
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if start_date and end_date:
                cursor.execute('''
                    SELECT * FROM attendance
                    WHERE student_id = ? AND date BETWEEN ? AND ?
                    ORDER BY date DESC
                ''', (student_id, start_date, end_date))
            else:
                cursor.execute('''
                    SELECT * FROM attendance
                    WHERE student_id = ?
                    ORDER BY date DESC
                ''', (student_id,))
            
            records = cursor.fetchall()
            conn.close()
            
            return [dict(record) for record in records]
        except sqlite3.Error as e:
            logger.error(f"Error fetching student attendance: {e}")
            return []
    
    def get_attendance_statistics(self, start_date=None, end_date=None):
        """
        Get attendance statistics.
        
        Args:
            start_date (str): Start date (optional)
            end_date (str): End date (optional)
            
        Returns:
            dict: Attendance statistics
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            clauses = []
            params = []
            if start_date and end_date:
                clauses.append("date BETWEEN ? AND ?")
                params.extend([start_date, end_date])
            
            # Total present
            present_clause = " AND ".join(clauses + ["status = ?"])
            cursor.execute(f'''
                SELECT COUNT(*) as count FROM attendance
                WHERE {present_clause}
            ''', tuple(params + ['Present']))
            total_present = cursor.fetchone()['count']
            
            # Total absent
            absent_clause = " AND ".join(clauses + ["status = ?"])
            cursor.execute(f'''
                SELECT COUNT(*) as count FROM attendance
                WHERE {absent_clause}
            ''', tuple(params + ['Absent']))
            total_absent = cursor.fetchone()['count']
            
            # Total late
            late_clause = " AND ".join(clauses + ["status = ?"])
            cursor.execute(f'''
                SELECT COUNT(*) as count FROM attendance
                WHERE {late_clause}
            ''', tuple(params + ['Late']))
            total_late = cursor.fetchone()['count']
            
            conn.close()
            
            return {
                'total_present': total_present,
                'total_absent': total_absent,
                'total_late': total_late,
                'total_records': total_present + total_absent + total_late
            }
        except sqlite3.Error as e:
            logger.error(f"Error getting attendance statistics: {e}")
            return {}
    
    def delete_attendance_record(self, record_id):
        """
        Delete an attendance record.
        
        Args:
            record_id (int): Attendance record ID
            
        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM attendance WHERE id = ?', (record_id,))
            conn.commit()
            conn.close()
            
            logger.info(f"Attendance record deleted: {record_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error deleting attendance record: {e}")
            return False
    
    # ================== DATABASE MAINTENANCE ==================
    def clear_all_data(self):
        """
        Clear all data from database (WARNING: irreversible).
        
        Returns:
            bool: True if cleared, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM attendance')
            cursor.execute('DELETE FROM users')
            
            conn.commit()
            conn.close()
            
            logger.warning("All database data cleared!")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error clearing database: {e}")
            return False
    
    def get_database_size(self):
        """
        Get database file size in MB.
        
        Returns:
            float: Database size in MB
        """
        try:
            size_bytes = self.db_file.stat().st_size
            return round(size_bytes / (1024 * 1024), 2)
        except Exception as e:
            logger.error(f"Error getting database size: {e}")
            return 0.0
    
    def vacuum_database(self):
        """
        Optimize database by removing unused space.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self.get_connection()
            conn.execute('VACUUM')
            conn.close()
            
            logger.info("Database vacuumed successfully")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error vacuuming database: {e}")
            return False


# Create global database manager instance
db_manager = DatabaseManager()
