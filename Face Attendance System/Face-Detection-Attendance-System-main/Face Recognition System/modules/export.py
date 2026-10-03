"""
CSV Export Module
Handles exporting attendance and user data to CSV
"""

import csv
import logging
from datetime import datetime
from pathlib import Path
from config import EXPORTS_DIR
from utils.database import db_manager
from utils.utils import ensure_directory_exists, get_current_date

logger = logging.getLogger(__name__)

class CSVExporter:
    """
    Handles exporting data to CSV files.
    """
    
    @staticmethod
    def export_attendance(start_date=None, end_date=None, filename=None):
        """
        Export attendance records to CSV.
        
        Args:
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
            filename (str): Custom filename (optional)
            
        Returns:
            dict: Export result with file path
        """
        try:
            ensure_directory_exists(EXPORTS_DIR)
            
            # Generate filename
            if not filename:
                if start_date and end_date:
                    filename = f"attendance_{start_date}_{end_date}.csv"
                else:
                    filename = f"attendance_{get_current_date()}.csv"
            
            filepath = EXPORTS_DIR / filename
            
            # Get attendance data
            if start_date and end_date:
                records = db_manager.get_attendance_by_date_range(start_date, end_date)
            else:
                records = db_manager.get_today_attendance()
            
            if not records:
                return {'success': False, 'message': 'No records to export'}
            
            # Write to CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['ID', 'Student ID', 'Name', 'Date', 'Time', 'Status', 'Confidence']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for i, record in enumerate(records, 1):
                    writer.writerow({
                        'ID': i,
                        'Student ID': record['student_id'],
                        'Name': record['name'],
                        'Date': record['date'],
                        'Time': record['time'],
                        'Status': record['status'],
                        'Confidence': f"{record.get('confidence', 0)*100:.2f}%"
                    })
            
            logger.info(f"Attendance exported to: {filepath}")
            return {
                'success': True,
                'message': f'Exported {len(records)} records',
                'filepath': str(filepath),
                'record_count': len(records)
            }
            
        except Exception as e:
            logger.error(f"Error exporting attendance: {e}")
            return {'success': False, 'message': f'Export failed: {str(e)}'}
    
    @staticmethod
    def export_users(filename=None):
        """
        Export all registered users to CSV.
        
        Args:
            filename (str): Custom filename (optional)
            
        Returns:
            dict: Export result with file path
        """
        try:
            ensure_directory_exists(EXPORTS_DIR)
            
            # Generate filename
            if not filename:
                filename = f"users_{get_current_date()}.csv"
            
            filepath = EXPORTS_DIR / filename
            
            # Get users
            users = db_manager.get_all_users()
            
            if not users:
                return {'success': False, 'message': 'No users to export'}
            
            # Write to CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['ID', 'Name', 'Student ID', 'Email', 'Phone', 'Registered Date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for i, user in enumerate(users, 1):
                    writer.writerow({
                        'ID': i,
                        'Name': user['name'],
                        'Student ID': user['student_id'],
                        'Email': user.get('email', ''),
                        'Phone': user.get('phone', ''),
                        'Registered Date': user.get('created_at', '')
                    })
            
            logger.info(f"Users exported to: {filepath}")
            return {
                'success': True,
                'message': f'Exported {len(users)} users',
                'filepath': str(filepath),
                'user_count': len(users)
            }
            
        except Exception as e:
            logger.error(f"Error exporting users: {e}")
            return {'success': False, 'message': f'Export failed: {str(e)}'}
    
    @staticmethod
    def export_attendance_summary(start_date=None, end_date=None, filename=None):
        """
        Export attendance summary (user-wise) to CSV.
        
        Args:
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
            filename (str): Custom filename (optional)
            
        Returns:
            dict: Export result with file path
        """
        try:
            ensure_directory_exists(EXPORTS_DIR)
            
            # Generate filename
            if not filename:
                if start_date and end_date:
                    filename = f"attendance_summary_{start_date}_{end_date}.csv"
                else:
                    filename = f"attendance_summary_{get_current_date()}.csv"
            
            filepath = EXPORTS_DIR / filename
            
            # Get all users
            users = db_manager.get_all_users()
            
            if not users:
                return {'success': False, 'message': 'No users to export'}
            
            # Collect attendance data for each user
            summary_data = []
            
            for user in users:
                student_id = user['student_id']
                
                # Get user's attendance
                attendance = db_manager.get_attendance_by_student(
                    student_id,
                    start_date,
                    end_date
                )
                
                present_count = sum(1 for a in attendance if a['status'] == 'Present')
                absent_count = sum(1 for a in attendance if a['status'] == 'Absent')
                late_count = sum(1 for a in attendance if a['status'] == 'Late')
                total_count = len(attendance)
                
                percentage = (present_count / total_count * 100) if total_count > 0 else 0
                
                summary_data.append({
                    'name': user['name'],
                    'student_id': student_id,
                    'total': total_count,
                    'present': present_count,
                    'absent': absent_count,
                    'late': late_count,
                    'percentage': f"{percentage:.2f}%"
                })
            
            # Write to CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Name', 'Student ID', 'Total Days', 'Present', 'Absent', 'Late', 'Attendance %']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for record in summary_data:
                    writer.writerow({
                        'Name': record['name'],
                        'Student ID': record['student_id'],
                        'Total Days': record['total'],
                        'Present': record['present'],
                        'Absent': record['absent'],
                        'Late': record['late'],
                        'Attendance %': record['percentage']
                    })
            
            logger.info(f"Attendance summary exported to: {filepath}")
            return {
                'success': True,
                'message': f'Exported summary for {len(summary_data)} users',
                'filepath': str(filepath),
                'user_count': len(summary_data)
            }
            
        except Exception as e:
            logger.error(f"Error exporting attendance summary: {e}")
            return {'success': False, 'message': f'Export failed: {str(e)}'}
    
    @staticmethod
    def get_export_files():
        """
        Get list of all exported files.
        
        Returns:
            list: List of export file information
        """
        try:
            ensure_directory_exists(EXPORTS_DIR)
            
            files = []
            for filepath in EXPORTS_DIR.glob("*.csv"):
                stat = filepath.stat()
                files.append({
                    'name': filepath.name,
                    'path': str(filepath),
                    'size': f"{stat.st_size / 1024:.2f} KB",
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })
            
            return sorted(files, key=lambda x: x['modified'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting export files: {e}")
            return []


# Create global exporter instance
csv_exporter = CSVExporter()
