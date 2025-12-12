"""
PostgreSQL Client for storing user profiles
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# PostgreSQL connection
_pg_connection = None
_pg_cursor = None

def get_postgres_client():
    """Get or create PostgreSQL client connection"""
    global _pg_connection, _pg_cursor
    
    if _pg_connection is None:
        try:
            import psycopg2
            from psycopg2 import sql, extras
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            
            # Get PostgreSQL connection string from environment
            postgres_uri = os.environ.get("POSTGRES_URI", "postgresql://localhost:5432/resumematchai")
            
            logger.info(f"Connecting to PostgreSQL: {postgres_uri}")
            _pg_connection = psycopg2.connect(postgres_uri)
            _pg_cursor = _pg_connection.cursor(cursor_factory=extras.RealDictCursor)
            
            # Test connection
            _pg_cursor.execute("SELECT version();")
            version = _pg_cursor.fetchone()
            logger.info(f"Successfully connected to PostgreSQL: {version['version']}")
            
            # Create schema if it doesn't exist
            _create_schema()
            
            return _pg_connection, _pg_cursor
            
        except ImportError:
            logger.error("psycopg2 not installed. Install with: pip install psycopg2-binary")
            raise ImportError("psycopg2 package is required. Install with: pip install psycopg2-binary")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
            raise ConnectionError(f"Could not connect to PostgreSQL. Please check your connection string and ensure PostgreSQL is running. Error: {str(e)}")
    
    return _pg_connection, _pg_cursor

def _create_schema():
    """Create database schema if it doesn't exist"""
    try:
        conn, cursor = get_postgres_client()
        
        # Create user_profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id SERIAL PRIMARY KEY,
                personal_info JSONB,
                summary TEXT,
                skills TEXT[],
                experience JSONB,
                education JSONB,
                certifications TEXT[],
                projects JSONB,
                languages TEXT[],
                awards TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create index on email for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_profiles_email 
            ON user_profiles ((personal_info->>'email'));
        """)
        
        # Create index on created_at for chronological queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_profiles_created_at 
            ON user_profiles (created_at DESC);
        """)
        
        conn.commit()
        logger.info("Database schema created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create schema: {str(e)}")
        if conn:
            conn.rollback()
        raise

def save_user_profile(profile_data: Dict[str, Any], collection_name: str = "user_profiles") -> Optional[int]:
    """
    Save user profile to PostgreSQL
    
    Args:
        profile_data: Dictionary containing user profile information
        collection_name: Name of the table (default: "user_profiles")
    
    Returns:
        int: Profile ID if successful, None if failed
    """
    try:
        conn, cursor = get_postgres_client()
        
        # Extract fields from profile_data
        personal_info = json.dumps(profile_data.get('personal_info', {}))
        summary = profile_data.get('summary', '')
        skills = profile_data.get('skills', [])
        experience = json.dumps(profile_data.get('experience', []))
        education = json.dumps(profile_data.get('education', []))
        certifications = profile_data.get('certifications', [])
        projects = json.dumps(profile_data.get('projects', []))
        languages = profile_data.get('languages', [])
        awards = profile_data.get('awards', [])
        
        # Insert profile
        cursor.execute("""
            INSERT INTO user_profiles 
            (personal_info, summary, skills, experience, education, certifications, projects, languages, awards, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            personal_info,
            summary,
            skills,
            experience,
            education,
            certifications,
            projects,
            languages,
            awards,
            datetime.utcnow(),
            datetime.utcnow()
        ))
        
        profile_id = cursor.fetchone()['id']
        conn.commit()
        
        logger.info(f"User profile saved successfully with ID: {profile_id}")
        return profile_id
        
    except Exception as e:
        logger.error(f"Failed to save user profile: {str(e)}")
        if conn:
            conn.rollback()
        return None

def update_user_profile(profile_id: int, profile_data: Dict[str, Any], collection_name: str = "user_profiles") -> bool:
    """
    Update existing user profile in PostgreSQL
    
    Args:
        profile_id: Profile ID
        profile_data: Dictionary containing updated profile information
        collection_name: Name of the table (default: "user_profiles")
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn, cursor = get_postgres_client()
        
        # Extract fields from profile_data
        personal_info = json.dumps(profile_data.get('personal_info', {}))
        summary = profile_data.get('summary', '')
        skills = profile_data.get('skills', [])
        experience = json.dumps(profile_data.get('experience', []))
        education = json.dumps(profile_data.get('education', []))
        certifications = profile_data.get('certifications', [])
        projects = json.dumps(profile_data.get('projects', []))
        languages = profile_data.get('languages', [])
        awards = profile_data.get('awards', [])
        
        # Update profile
        cursor.execute("""
            UPDATE user_profiles
            SET personal_info = %s,
                summary = %s,
                skills = %s,
                experience = %s,
                education = %s,
                certifications = %s,
                projects = %s,
                languages = %s,
                awards = %s,
                updated_at = %s
            WHERE id = %s;
        """, (
            personal_info,
            summary,
            skills,
            experience,
            education,
            certifications,
            projects,
            languages,
            awards,
            datetime.utcnow(),
            profile_id
        ))
        
        rows_affected = cursor.rowcount
        conn.commit()
        
        if rows_affected > 0:
            logger.info(f"User profile updated successfully: {profile_id}")
            return True
        else:
            logger.warning(f"No profile found with ID: {profile_id}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to update user profile: {str(e)}")
        if conn:
            conn.rollback()
        return False

def get_user_profile(profile_id: int, collection_name: str = "user_profiles") -> Optional[Dict[str, Any]]:
    """
    Retrieve user profile from PostgreSQL
    
    Args:
        profile_id: Profile ID
        collection_name: Name of the table (default: "user_profiles")
    
    Returns:
        dict: User profile data if found, None otherwise
    """
    try:
        conn, cursor = get_postgres_client()
        
        cursor.execute("""
            SELECT id, personal_info, summary, skills, experience, education, 
                   certifications, projects, languages, awards, created_at, updated_at
            FROM user_profiles
            WHERE id = %s;
        """, (profile_id,))
        
        row = cursor.fetchone()
        
        if row:
            # Convert row to dictionary and parse JSON fields
            profile = dict(row)
            profile['personal_info'] = json.loads(profile['personal_info']) if profile['personal_info'] else {}
            profile['experience'] = json.loads(profile['experience']) if profile['experience'] else []
            profile['education'] = json.loads(profile['education']) if profile['education'] else []
            profile['projects'] = json.loads(profile['projects']) if profile['projects'] else []
            
            # Convert datetime to string for JSON serialization
            profile['created_at'] = profile['created_at'].isoformat() if profile['created_at'] else None
            profile['updated_at'] = profile['updated_at'].isoformat() if profile['updated_at'] else None
            
            return profile
        else:
            logger.warning(f"No profile found with ID: {profile_id}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to retrieve user profile: {str(e)}")
        return None

def find_profiles_by_email(email: str, collection_name: str = "user_profiles") -> List[Dict[str, Any]]:
    """
    Find user profiles by email address
    
    Args:
        email: Email address to search for
        collection_name: Name of the table (default: "user_profiles")
    
    Returns:
        list: List of matching profiles
    """
    try:
        conn, cursor = get_postgres_client()
        
        cursor.execute("""
            SELECT id, personal_info, summary, skills, experience, education, 
                   certifications, projects, languages, awards, created_at, updated_at
            FROM user_profiles
            WHERE personal_info->>'email' = %s;
        """, (email,))
        
        rows = cursor.fetchall()
        profiles = []
        
        for row in rows:
            profile = dict(row)
            profile['personal_info'] = json.loads(profile['personal_info']) if profile['personal_info'] else {}
            profile['experience'] = json.loads(profile['experience']) if profile['experience'] else []
            profile['education'] = json.loads(profile['education']) if profile['education'] else []
            profile['projects'] = json.loads(profile['projects']) if profile['projects'] else []
            
            # Convert datetime to string for JSON serialization
            profile['created_at'] = profile['created_at'].isoformat() if profile['created_at'] else None
            profile['updated_at'] = profile['updated_at'].isoformat() if profile['updated_at'] else None
            
            profiles.append(profile)
        
        return profiles
        
    except Exception as e:
        logger.error(f"Failed to search profiles by email: {str(e)}")
        return []

def test_connection() -> bool:
    """Test PostgreSQL connection"""
    try:
        conn, cursor = get_postgres_client()
        cursor.execute("SELECT 1;")
        cursor.fetchone()
        return True
    except Exception as e:
        logger.error(f"PostgreSQL connection test failed: {str(e)}")
        return False
