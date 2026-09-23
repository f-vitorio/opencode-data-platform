#!/usr/bin/env python3
"""
YouTube Growth Manager for OpenCode
Consumes output from video-creator skill to manage YouTube Shorts channel
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import urllib.parse

# Google API imports
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    print("Warning: Google API libraries not installed. Install with:")
    print("pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")

# Constants
VIDEO_MAKER_DIR = Path("/home/fvitorio/Videos/video-maker")
CREDENTIALS_DIR = Path("/home/fvitorio/.config/opencode/credentials")
TOKEN_FILE = CREDENTIALS_DIR / "youtube-token.json"
CLIENT_SECRETS_FILE = CREDENTIALS_DIR / "client_secret_1096436543776-iuo52suml8tgdtgvfalnbf15rhmq8kfk.apps.googleusercontent.com.json"
HISTORY_FILE = Path("/home/fvitorio/.config/opencode/skills/youtube-growth/history.json")

# Delimiter used in video-creator metadata files (63 ═ characters)
DELIMITER = "═" * 63

# YouTube API scopes
SCOPES = [
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/yt-analytics.readonly',
]

class YouTubeGrowthManager:
    def __init__(self):
        self.credentials = None
        self.youtube_service = None
        self.analytics_service = None
        self.history = self.load_history()
        
        # Ensure directories exist
        CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    def authenticate(self):
        """Authenticate with YouTube API"""
        if not GOOGLE_API_AVAILABLE:
            raise Exception("Google API libraries not available")
        
        creds = None
        
        # Load existing token
        if TOKEN_FILE.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            except Exception as e:
                print(f"Error loading token: {e}")
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    creds = None
            if not creds:
                if not CLIENT_SECRETS_FILE.exists():
                    raise Exception(
                        f"Client secrets file not found: {CLIENT_SECRETS_FILE}\n"
                        "Please download OAuth 2.0 credentials from Google Cloud Console"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CLIENT_SECRETS_FILE), SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        
        self.credentials = creds
        self.youtube_service = build('youtube', 'v3', credentials=creds)
        self.analytics_service = build('youtubeAnalytics', 'v2', credentials=creds)
        
        print("[YouTube] Authentication successful")
        return True
    
    def load_history(self) -> Dict:
        """Load upload history from JSON file"""
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load history file: {e}")
                return {}
        return {}
    
    def generate_utm_url(self, video_id: str, niche: str = "marketing") -> str:
        """
        Generate URL with UTM parameters for GA4 tracking
        
        Args:
            video_id: YouTube video ID
            niche: Content niche (clinicas, advogados, contadores, etc.)
            
        Returns:
            URL with UTM parameters
        """
        base_url = "https://fvs7.com.br/diagnostico-gratuito"
        utm_params = f"utm_source=youtube&utm_medium=shorts&utm_campaign={video_id}&utm_content={niche}"
        return f"{base_url}?{utm_params}"
    
    def add_utm_to_description(self, description: str, video_id: str, niche: str = "marketing") -> str:
        """
        Add UTM link to video description if not already present
        
        Args:
            description: Original description
            video_id: YouTube video ID
            niche: Content niche
            
        Returns:
            Description with UTM link
        """
        utm_url = self.generate_utm_url(video_id, niche)
        
        # Check if UTM already exists
        if "utm_source=youtube" in description:
            return description
        
        # Check if there's a link to replace
        if "fvs7.com.br/diagnostico-gratuito" in description:
            # Replace existing link with UTM version
            import re
            pattern = r'https?://fvs7\.com\.br/diagnostico-gratuito(?:\?[^\s]*)?'
            replacement = utm_url
            description = re.sub(pattern, replacement, description)
        else:
            # Add UTM link at the end
            description = f"{description}\n\n👉 Diagnóstico Grátis: {utm_url}"
        
        return description
    
    def detect_niche_from_title(self, title: str) -> str:
        """
        Detect content niche from video title
        
        Args:
            title: Video title
            
        Returns:
            Niche slug for utm_content
        """
        title_lower = title.lower()
        
        niche_keywords = {
            "clinicas": ["clínica", "clínicas", "estética", "agendamento", "paciente"],
            "advogados": ["advogado", "advogados", "jurídico", "jurídica", "escritório"],
            "contadores": ["contador", "contadores", "contabilidade", "pj"],
            "fisioterapeutas": ["fisioterapeuta", "fisioterapia", "fisioterapeutas"],
            "psicologos": ["psicólogo", "psicólogos", "psicologia", "terapia"],
            "imobiliarias": ["imobiliária", "imobiliárias", "corretor", "imóvel"],
            "esteticistas": ["esteticista", "esteticistas", "estética"],
            "negocios_locais": ["negócio local", "negócios locais", "comércio", "região"],
            "landing_pages": ["landing page", "landing pages", "conversão", "cro"],
            "tracking": ["tracking", "conversão", "ga4", "gtm", "analytics"],
            "marketing": ["marketing", "google ads", "tráfego", "anúncio"]
        }
        
        for niche, keywords in niche_keywords.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return niche
        
        return "marketing"
    
    def save_history(self):
        """Save upload history to JSON file"""
        try:
            with open(HISTORY_FILE, 'w') as f:
                json.dump(self.history, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def find_video_files(self, video_name: Optional[str] = None) -> List[Tuple[Path, Path]]:
        """
        Find video and metadata file pairs in the video-maker directory
        
        Args:
            video_name: Optional specific name to search for (without extension)
            
        Returns:
            List of tuples (video_path, metadata_path)
        """
        pairs = []
        
        if video_name:
            # Search for specific video
            video_path = VIDEO_MAKER_DIR / f"{video_name}.mp4"
            metadata_path = VIDEO_MAKER_DIR / f"{video_name}.txt"
            if video_path.exists() and metadata_path.exists():
                pairs.append((video_path, metadata_path))
            else:
                print(f"[YouTube] Video pair not found for '{video_name}'")
                print(f"  Looking for: {video_path} and {metadata_path}")
        else:
            # Find all video-mp4 files and look for corresponding txt files
            for video_path in VIDEO_MAKER_DIR.glob("*.mp4"):
                metadata_path = VIDEO_MAKER_DIR / f"{video_path.stem}.txt"
                if metadata_path.exists():
                    pairs.append((video_path, metadata_path))
                else:
                    print(f"[YouTube] Warning: Metadata file not found for {video_path.name}")
        
        return pairs
    
    def parse_metadata_file(self, metadata_path: Path) -> Dict[str, str]:
        """
        Parse the metadata .txt file generated by video-creator
        
        Args:
            metadata_path: Path to the .txt file
            
        Returns:
            Dictionary with keys: title, description, hashtags
        """
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise Exception(f"Error reading metadata file {metadata_path}: {e}")
        
        # Extract title (allows optional blank lines before closing delimiter)
        title_pattern = (
            DELIMITER + '\n' +
            r'TÍTULO \(para YouTube Shorts / Reels / TikTok\)\n' +
            DELIMITER + '\n' +
            r'([\s\S]*?)\n\s*' +
            DELIMITER
        )
        title_match = re.search(title_pattern, content)
        title = title_match.group(1).strip() if title_match else ""
        
        # Extract description
        desc_pattern = (
            DELIMITER + '\n' +
            r'DESCRIÇÃO \(copie e cole\)\n' +
            DELIMITER + '\n' +
            r'([\s\S]*?)\n\s*' +
            DELIMITER
        )
        desc_match = re.search(desc_pattern, content)
        description = desc_match.group(1).strip() if desc_match else ""
        
        # Extract hashtags
        hashtags_pattern = (
            DELIMITER + '\n' +
            r'HASHTAGS \(para usar nos comentários ou descrição\)\n' +
            DELIMITER + '\n' +
            r'([\s\S]*?)\n\s*' +
            DELIMITER
        )
        hashtags_match = re.search(hashtags_pattern, content)
        hashtags_raw = hashtags_match.group(1).strip() if hashtags_match else ""
        # Clean up hashtags - extract just the tags
        if hashtags_raw:
            # Extract hashtags from lines that start with #
            hashtag_lines = [line.strip() for line in hashtags_raw.split('\n') if line.strip().startswith('#')]
            hashtags = ' '.join(hashtag_lines)
        else:
            hashtags = ""
        
        return {
            'title': title,
            'description': description,
            'hashtags': hashtags
        }
    
    def is_video_already_uploaded(self, video_path: Path) -> bool:
        """Check if a video has already been uploaded based on history"""
        video_stem = video_path.stem
        if video_stem in self.history:
            entry = self.history[video_stem]
            if entry.get('video_id') and entry.get('status') in ['uploaded', 'published', 'scheduled']:
                # Double-check with YouTube API if possible
                try:
                    if self.youtube_service:
                        response = self.youtube_service.videos().list(
                            part='status',
                            id=entry['video_id']
                        ).execute()
                        
                        if response.get('items'):
                            return True
                except Exception:
                    # If we can't verify, assume it's uploaded based on history
                    return True
        return False
    
    def upload_video(self, video_path: Path, metadata_path: Path, 
                     scheduled_time: Optional[datetime] = None) -> Dict:
        """
        Upload a video to YouTube
        
        Args:
            video_path: Path to the .mp4 video file
            metadata_path: Path to the .txt metadata file
            scheduled_time: Optional datetime for scheduling the upload
            
        Returns:
            Dictionary with upload results
        """
        # Authenticate if needed
        if not self.youtube_service:
            self.authenticate()
        
        # Check if already uploaded
        if self.is_video_already_uploaded(video_path):
            video_stem = video_path.stem
            existing_entry = self.history.get(video_stem, {})
            print(f"[YouTube] Video already uploaded: {video_stem}")
            print(f"  Video ID: {existing_entry.get('video_id')}")
            print(f"  Status: {existing_entry.get('status')}")
            return existing_entry
        
        # Parse metadata
        try:
            metadata = self.parse_metadata_file(metadata_path)
        except Exception as e:
            raise Exception(f"Failed to parse metadata: {e}")
        
        if not metadata['title']:
            raise Exception("No title found in metadata file")
        
        # Detect niche and add UTM to description
        niche = self.detect_niche_from_title(metadata['title'])
        description_with_utm = self.add_utm_to_description(
            metadata['description'], 
            "TEMP_ID",  # Will be replaced after upload
            niche
        )
        
        # Prepare video metadata for YouTube
        body = {
            'snippet': {
                'title': metadata['title'],
                'description': description_with_utm,
                'tags': self._extract_tags_from_hashtags(metadata['hashtags']),
                'categoryId': '27'  # Education category - adjust as needed
            },
            'status': {
                'privacyStatus': 'private' if scheduled_time else 'private',  # Will change based on scheduling
                'selfDeclaredMadeForKids': False
            }
        }
        
        # If scheduling is requested, set the publish time
        if scheduled_time:
            # YouTube requires RFC 3339 format
            body['status']['publishAt'] = scheduled_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            body['status']['privacyStatus'] = 'private'  # Scheduled videos start as private
        
        print(f"[YouTube] Upload started: {metadata['title']}")
        if scheduled_time:
            print(f"[YouTube] Scheduled for: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Upload the video
        try:
            media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
            
            insert_request = self.youtube_service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            error = None
            retry = 0
            
            while response is None:
                try:
                    status, response = insert_request.next_chunk()
                    if status:
                        print(f"[YouTube] Uploaded {int(status.progress() * 100)}%")
                except Exception as e:
                    if retry < 3:
                        retry += 1
                        print(f"[YouTube] Upload error, retrying ({retry}/3): {e}")
                        continue
                    else:
                        raise e
            
            if response is not None:
                video_id = response['id']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                # Generate final description with actual video_id
                final_description = self.add_utm_to_description(
                    metadata['description'],
                    video_id,
                    niche
                )
                
                # Update the video description with actual UTM
                try:
                    self.youtube_service.videos().update(
                        part='snippet',
                        body={
                            'id': video_id,
                            'snippet': {
                                'title': metadata['title'],
                                'description': final_description,
                                'tags': self._extract_tags_from_hashtags(metadata['hashtags']),
                                'categoryId': '27'
                            }
                        }
                    ).execute()
                except Exception as e:
                    print(f"[YouTube] Warning: Could not update description with UTM: {e}")
                
                # Update history
                video_stem = video_path.stem
                history_entry = {
                    'video_id': video_id,
                    'video_file': str(video_path),
                    'metadata_file': str(metadata_path),
                    'title': metadata['title'],
                    'description': final_description,
                    'hashtags': metadata['hashtags'],
                    'youtube_url': video_url,
                    'uploaded_at': datetime.now().isoformat(),
                    'scheduled_at': scheduled_time.isoformat() if scheduled_time else None,
                    'published_at': None,
                    'status': 'scheduled' if scheduled_time else 'uploaded',
                    'privacy_status': body['status']['privacyStatus']
                }
                
                self.history[video_stem] = history_entry
                self.save_history()
                
                print(f"[YouTube] Upload completed")
                print(f"[YouTube] Video ID: {video_id}")
                print(f"[YouTube] URL: {video_url}")
                
                if scheduled_time:
                    print(f"[YouTube] Scheduled for: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                
                return history_entry
            
        except Exception as e:
            print(f"[YouTube] Upload failed: {e}")
            raise
    
    def _extract_tags_from_hashtags(self, hashtags_str: str) -> List[str]:
        """Extract tags from hashtags string for YouTube upload"""
        if not hashtags_str:
            return []
        
        # Extract words that start with # and remove the #
        tags = []
        for word in hashtags_str.split():
            if word.startswith('#'):
                tag = word[1:]  # Remove the #
                # YouTube tags have restrictions: max 30 chars, no commas, etc.
                if len(tag) <= 30 and ',' not in tag:
                    tags.append(tag)
        
        # Limit to reasonable number of tags (YouTube allows up to 500 characters total)
        return tags[:10]  # Conservative limit
    
    def list_scheduled_videos(self) -> List[Dict]:
        """List all scheduled videos from history"""
        scheduled = []
        for video_stem, entry in self.history.items():
            if entry.get('status') == 'scheduled' and entry.get('scheduled_at'):
                scheduled.append(entry)
        
        # Sort by scheduled time
        scheduled.sort(key=lambda x: x.get('scheduled_at', ''))
        return scheduled
    
    def get_video_status(self, video_id: str) -> Dict:
        """Get current status of a video from YouTube API"""
        if not self.youtube_service:
            self.authenticate()
        
        try:
            response = self.youtube_service.videos().list(
                part='status,snippet',
                id=video_id
            ).execute()
            
            if response.get('items'):
                item = response['items'][0]
                return {
                    'video_id': video_id,
                    'title': item['snippet'].get('title'),
                    'description': item['snippet'].get('description'),
                    'tags': item['snippet'].get('tags', []),
                    'privacy_status': item['status'].get('privacyStatus'),
                    'publish_at': item['status'].get('publishAt'),
                    'uploaded_at': item['snippet'].get('publishedAt')
                }
            else:
                return {'error': 'Video not found'}
        except Exception as e:
            return {'error': str(e)}
    
    def cancel_scheduled_video(self, video_id: str) -> bool:
        """Cancel a scheduled video by changing its privacy status back to private"""
        if not self.youtube_service:
            self.authenticate()
        
        try:
            # First get current video details
            video_info = self.get_video_status(video_id)
            if 'error' in video_info:
                print(f"[YouTube] Error getting video info: {video_info['error']}")
                return False
            
            # Update the video to remove scheduled time and set to private
            update_body = {
                'id': video_id,
                'snippet': {
                    'title': video_info['title'],
                    'description': video_info['description'],
                    'tags': video_info.get('tags', []),
                    'categoryId': '27'
                },
                'status': {
                    'privacyStatus': 'private',
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Remove publishAt field to cancel scheduling
            if 'publishAt' in update_body['status']:
                del update_body['status']['publishAt']
            
            self.youtube_service.videos().update(
                part='snippet,status',
                body=update_body
            ).execute()
            
            # Update history
            for video_stem, entry in self.history.items():
                if entry.get('video_id') == video_id:
                    entry['status'] = 'uploaded'  # Back to uploaded but not scheduled
                    entry['scheduled_at'] = None
                    entry['privacy_status'] = 'private'
                    break
            
            self.save_history()
            print(f"[YouTube] Scheduled publication cancelled for video {video_id}")
            return True
            
        except Exception as e:
            print(f"[YouTube] Error cancelling scheduled video: {e}")
            return False
    
    def publish_now(self, video_id: str) -> bool:
        """Publish a scheduled video immediately"""
        if not self.youtube_service:
            self.authenticate()
        
        try:
            # Get current video details
            video_info = self.get_video_status(video_id)
            if 'error' in video_info:
                print(f"[YouTube] Error getting video info: {video_info['error']}")
                return False
            
            # Update the video to public (immediate publish)
            update_body = {
                'id': video_id,
                'snippet': {
                    'title': video_info['title'],
                    'description': video_info['description'],
                    'tags': video_info.get('tags', []),
                    'categoryId': '27'
                },
                'status': {
                    'privacyStatus': 'public',
                    'selfDeclaredMadeForKids': False,
                }
            }
            
            self.youtube_service.videos().update(
                part='snippet,status',
                body=update_body
            ).execute()
            
            # Update history
            for video_stem, entry in self.history.items():
                if entry.get('video_id') == video_id:
                    entry['status'] = 'published'
                    entry['published_at'] = datetime.now().isoformat()
                    entry['privacy_status'] = 'public'
                    break
            
            self.save_history()
            print(f"[YouTube] Video {video_id} published immediately")
            return True
            
        except Exception as e:
            import traceback
            print(f"[YouTube] Error publishing video immediately: {e}")
            print(f"[YouTube] Exception type: {type(e)}")
            traceback.print_exc()
            return False

    def schedule_existing_publish(self, video_id: str, scheduled_time: datetime) -> bool:
        """
        Schedule an already-uploaded (private) video to be published at a future time.
        Sets privacyStatus=private + publishAt so YouTube publishes it automatically.

        Args:
            video_id: YouTube video ID (must already exist / be uploaded)
            scheduled_time: datetime when the video should go public

        Returns:
            True on success, False otherwise
        """
        if not self.youtube_service:
            self.authenticate()

        if scheduled_time <= datetime.now():
            print(f"[YouTube] Scheduled time is in the past: {scheduled_time}")
            return False

        try:
            # Get current video details (title/description/tags preserved)
            video_info = self.get_video_status(video_id)
            if 'error' in video_info:
                print(f"[YouTube] Error getting video info: {video_info['error']}")
                return False

            # Update the video to scheduled (private until publishAt)
            update_body = {
                'id': video_id,
                'snippet': {
                    'title': video_info['title'],
                    'description': video_info['description'],
                    'tags': video_info.get('tags', []),
                    'categoryId': '27'
                },
                'status': {
                    'privacyStatus': 'private',
                    'selfDeclaredMadeForKids': False,
                    'publishAt': scheduled_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
                }
            }

            self.youtube_service.videos().update(
                part='snippet,status',
                body=update_body
            ).execute()

            # Update history
            for video_stem, entry in self.history.items():
                if entry.get('video_id') == video_id:
                    entry['status'] = 'scheduled'
                    entry['scheduled_at'] = scheduled_time.isoformat()
                    entry['published_at'] = None
                    entry['privacy_status'] = 'private'
                    break

            self.save_history()
            print(f"[YouTube] Video {video_id} scheduled for {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
            return True

        except Exception as e:
            import traceback
            print(f"[YouTube] Error scheduling video: {e}")
            print(f"[YouTube] Exception type: {type(e)}")
            traceback.print_exc()
            return False

    def update_metadata(self, video_id: str, title: str, description: str, add_utm: bool = True) -> bool:
        """
        Update an existing video's title and description, preserving its current
        privacy status and schedule (publishAt) so scheduled videos stay scheduled
        and published videos stay public.

        Args:
            video_id: YouTube video ID
            title: New video title
            description: New video description
            add_utm: Whether to add UTM parameters to links (default: True)

        Returns:
            True on success, False otherwise
        """
        if not self.youtube_service:
            self.authenticate()

        try:
            video_info = self.get_video_status(video_id)
            if 'error' in video_info:
                print(f"[YouTube] Error getting video info: {video_info['error']}")
                return False

            # Add UTM to description if requested
            if add_utm:
                niche = self.detect_niche_from_title(title)
                description = self.add_utm_to_description(description, video_id, niche)

            # Preserve current privacy status + schedule
            status = {
                'privacyStatus': video_info.get('privacy_status', 'private'),
                'selfDeclaredMadeForKids': False,
            }
            if video_info.get('publish_at'):
                status['publishAt'] = video_info['publish_at']

            update_body = {
                'id': video_id,
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': video_info.get('tags', []),
                    'categoryId': '27'
                },
                'status': status
            }

            self.youtube_service.videos().update(
                part='snippet,status',
                body=update_body
            ).execute()

            # Update history
            for video_stem, entry in self.history.items():
                if entry.get('video_id') == video_id:
                    entry['title'] = title
                    entry['description'] = description
                    break

            self.save_history()
            print(f"[YouTube] Updated metadata for {video_id}: {title}")
            return True

        except Exception as e:
            import traceback
            print(f"[YouTube] Error updating metadata for {video_id}: {e}")
            print(f"[YouTube] Exception type: {type(e)}")
            traceback.print_exc()
            return False

    def add_comment(self, video_id: str, text: str) -> bool:
        """
        Add a comment to a YouTube video.

        Args:
            video_id: YouTube video ID
            text: Comment text (max 1000 chars)

        Returns:
            True on success, False otherwise
        """
        if not self.youtube_service:
            self.authenticate()

        try:
            # Truncate if too long
            if len(text) > 1000:
                text = text[:997] + "..."

            comment_body = {
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": text
                        }
                    }
                }
            }

            self.youtube_service.commentThreads().insert(
                part="snippet",
                body=comment_body
            ).execute()

            print(f"[YouTube] Comment added to {video_id}")
            return True

        except Exception as e:
            print(f"[YouTube] Error adding comment to {video_id}: {e}")
            return False

def natural_language_to_datetime(text: str) -> Optional[datetime]:
    """
    Convert natural language time expressions to datetime objects
    
    Supported formats:
    - "terça às 6AM" -> next Tuesday at 6:00 AM
    - "amanhã às 19h" -> tomorrow at 7:00 PM
    - "daqui a 2 semanas" -> in 2 weeks
    - "daqui a 15 dias" -> in 15 days
    - "segunda-feira" -> next Monday
    - "dia 15 às 08:00" -> 15th of current month at 08:00
    - "2 de outubro às 07:30" -> October 2nd at 07:30
    """
    # This is a simplified implementation - in a real scenario, you'd want
    # to use a more sophisticated date parser like dateutil
    text = text.lower().strip()
    now = datetime.now()
    
    # Handle "daqui a X semanas/dias"
    if text.startswith("daqui a "):
        try:
            parts = text[8:].split()
            if len(parts) >= 2:
                amount = int(parts[0])
                unit = parts[1]
                
                if unit.startswith("semana") or unit.startswith("semanas"):
                    return now + timedelta(weeks=amount)
                elif unit.startswith("dia") or unit.startswith("dias"):
                    return now + timedelta(days=amount)
        except (ValueError, IndexError):
            pass
    
    # Handle "amanhã"
    if text.startswith("amanhã"):
        base_date = now + timedelta(days=1)
        time_part = text[7:].strip()  # Fixed: was [8:], should be [7:] to skip "amanhã" + space
        if time_part.startswith("às ") or time_part.startswith("as "):
            time_str = time_part[3:].strip()
            return _parse_time_string(base_date, time_str)
        return base_date.replace(hour=9, minute=0, second=0, microsecond=0)  # Default 9 AM
    
    # Handle day names
    weekdays = {
        'segunda': 0, 'terça': 1, 'quarta': 2, 'quinta': 3,
        'sexta': 4, 'sábado': 5, 'domingo': 6
    }
    
    for day_name, day_num in weekdays.items():
        if text.startswith(day_name):
            days_ahead = day_num - now.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            
            base_date = now + timedelta(days=days_ahead)
            time_part = text[len(day_name)+1:].strip()  # Fixed: was [len(day_name):], need to skip the space too
            
            if time_part.startswith("às ") or time_part.startswith("as "):
                time_str = time_part[3:].strip()
                return _parse_time_string(base_date, time_str)
            
            return base_date.replace(hour=9, minute=0, second=0, microsecond=0)
    
    # Handle "dia X às HH:MM" format
    dia_match = re.search(r'dia\s+(\d+)\s+às\s+(.+)', text)
    if dia_match:
        try:
            day = int(dia_match.group(1))
            time_str = dia_match.group(2).strip()
            
            # Get current month/year
            base_date = now.replace(day=day, hour=0, minute=0, second=0, microsecond=0)
            
            # If the day has already passed this month, go to next month
            if base_date < now.replace(hour=0, minute=0, second=0, microsecond=0):
                if base_date.month == 12:
                    base_date = base_date.replace(year=now.year + 1, month=1)
                else:
                    base_date = base_date.replace(month=base_date.month + 1)
            
            return _parse_time_string(base_date, time_str)
        except (ValueError, IndexError):
            pass
    
    # Handle "X de mês às HH:MM" format
    month_match = re.search(r'(\d+)\s+de\s+(\w+)\s+às\s+(.+)', text)
    if month_match:
        try:
            day = int(month_match.group(1))
            month_name = month_match.group(2)
            time_str = month_match.group(3).strip()
            
            # Map month names to numbers
            months = {
                'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
                'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
                'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
            }
            
            if month_name in months:
                month = months[month_name]
                year = now.year
                
                # If the month has already passed this year, go to next year
                if month < now.month or (month == now.month and day < now.day):
                    year += 1
                
                base_date = now.replace(year=year, month=month, day=day, hour=0, minute=0, second=0, microsecond=0)
                return _parse_time_string(base_date, time_str)
        except (ValueError, IndexError, KeyError):
            pass
    
    # If we get here, we couldn't parse it
    return None

def _parse_time_string(base_date: datetime, time_str: str) -> datetime:
    """Parse time string and apply to base_date"""
    try:
        # Handle formats like "6AM", "19h", "08:00", "07:30"
        # Clean up the string
        time_str = time_str.strip().lower()
        
        # Handle AM/PM notation
        if 'am' in time_str or 'pm' in time_str:
            # Extract the number and AM/PN
            match = re.search(r'(\d+)\s*(am|pm)', time_str)
            if match:
                hour = int(match.group(1))
                am_pm = match.group(2)
                
                if am_pm == 'pm' and hour != 12:
                    hour += 12
                elif am_pm == 'am' and hour == 12:
                    hour = 0
                
                return base_date.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        # Handle "HHh" format
        if time_str.endswith('h'):
            hour = int(time_str[:-1])
            return base_date.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        # Handle "HH:MM" format
        if ':' in time_str:
            parts = time_str.split(':')
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0
            return base_date.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        # Handle just "HH" format
        hour = int(time_str)
        return base_date.replace(hour=hour, minute=0, second=0, microsecond=0)
    except (ValueError, IndexError):
        # Return default time if parsing fails
        return base_date.replace(hour=9, minute=0, second=0, microsecond=0)

def main():
    parser = argparse.ArgumentParser(description='YouTube Growth Manager for OpenCode')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload a video to YouTube')
    upload_parser.add_argument('video_name', nargs='?', help='Name of video file (without extension)')
    upload_parser.add_argument('--file', '-f', help='Path to video file')
    
    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Schedule a video for future publication')
    schedule_parser.add_argument('video_name', nargs='?', help='Name of video file (without extension)')
    schedule_parser.add_argument('--file', '-f', help='Path to video file')
    schedule_parser.add_argument('--when', '-w', required=True, help='When to publish (natural language)')
    
    # List schedule command
    subparsers.add_parser('schedule-list', help='List scheduled videos')
    
    # Cancel schedule command
    cancel_parser = subparsers.add_parser('schedule-cancel', help='Cancel a scheduled video')
    cancel_parser.add_argument('video_id', help='YouTube video ID to cancel')
    
    # Publish now command
    publish_parser = subparsers.add_parser('publish-now', help='Publish a scheduled video immediately')
    publish_parser.add_argument('video_id', help='YouTube video ID to publish')

    # Schedule existing command
    schedule_existing_parser = subparsers.add_parser(
        'schedule-existing',
        help='Schedule an already-uploaded private video for future publication'
    )
    schedule_existing_parser.add_argument('video_id', help='YouTube video ID to schedule')
    schedule_existing_parser.add_argument('--when', '-w', required=True,
                                          help='When to publish (natural language), e.g. "terça às 6AM"')
    
    # Analytics command
    analytics_parser = subparsers.add_parser('analytics', help='Show channel analytics')
    analytics_parser.add_argument('--days', '-d', type=int, default=30, help='Number of days to analyze')
    
    # Args for all commands
    parser.add_argument('--yes', '-y', action='store_true', help='Assume yes to prompts')
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = YouTubeGrowthManager()
    
    if args.command == 'upload':
        # Find video files
        if args.video_name:
            pairs = manager.find_video_files(args.video_name)
        elif args.file:
            video_path = Path(args.file)
            metadata_path = video_path.with_suffix('.txt')
            if video_path.exists() and metadata_path.exists():
                pairs = [(video_path, metadata_path)]
            else:
                print(f"[YouTube] Error: Video or metadata file not found")
                print(f"  Video: {video_path}")
                print(f"  Metadata: {metadata_path}")
                return 1
        else:
            pairs = manager.find_video_files()
        
        if not pairs:
            print("[YouTube] No video files found to upload")
            return 1
        
        if len(pairs) > 1 and not args.video_name and not args.file:
            print("[YouTube] Multiple video files found:")
            for i, (video_path, metadata_path) in enumerate(pairs):
                print(f"  {i+1}. {video_path.name}")
            print("Please specify which video to upload using --video-name or --file")
            return 1
        
        video_path, metadata_path = pairs[0]
        
        # Confirm upload
        if not args.yes:
            metadata = manager.parse_metadata_file(metadata_path)
            print(f"[YouTube] About to upload:")
            print(f"  Title: {metadata['title']}")
            print(f"  Description: {metadata['description'][:100]}..." if len(metadata['description']) > 100 else f"  Description: {metadata['description']}")
            print(f"  Hashtags: {metadata['hashtags']}")
            
            response = input("\nProceed with upload? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("[YouTube] Upload cancelled")
                return 0
        
        try:
            result = manager.upload_video(video_path, metadata_path)
            print(f"\n[YouTube] Upload successful!")
            print(f"  Video ID: {result['video_id']}")
            print(f"  URL: {result['youtube_url']}")
            return 0
        except Exception as e:
            print(f"[YouTube] Upload failed: {e}")
            return 1
    
    elif args.command == 'schedule':
        # Find video files
        if args.video_name:
            pairs = manager.find_video_files(args.video_name)
        elif args.file:
            video_path = Path(args.file)
            metadata_path = video_path.with_suffix('.txt')
            if video_path.exists() and metadata_path.exists():
                pairs = [(video_path, metadata_path)]
            else:
                print(f"[YouTube] Error: Video or metadata file not found")
                print(f"  Video: {video_path}")
                print(f"  Metadata: {metadata_path}")
                return 1
        else:
            pairs = manager.find_video_files()
        
        if not pairs:
            print("[YouTube] No video files found to schedule")
            return 1
        
        if len(pairs) > 1 and not args.video_name and not args.file:
            print("[YouTube] Multiple video files found:")
            for i, (video_path, metadata_path) in enumerate(pairs):
                print(f"  {i+1}. {video_path.name}")
            print("Please specify which video to schedule using --video-name or --file")
            return 1
        
        video_path, metadata_path = pairs[0]
        
        # Parse natural language time
        scheduled_time = natural_language_to_datetime(args.when)
        if not scheduled_time:
            print(f"[YouTube] Could not parse time expression: '{args.when}'")
            print("Please use formats like:")
            print("  'terça às 6AM'")
            print("  'amanhã às 19h'")
            print("  'daqui a 2 semanas'")
            print("  'segunda-feira'")
            print("  'dia 15 às 08:00'")
            print("  '2 de outubro às 07:30'")
            return 1
        
        # Check if time is in the past
        if scheduled_time < datetime.now():
            print(f"[YouTube] Scheduled time is in the past: {scheduled_time}")
            return 1
        
        # Confirm scheduling
        if not args.yes:
            metadata = manager.parse_metadata_file(metadata_path)
            print(f"[YouTube] About to schedule:")
            print(f"  Title: {metadata['title']}")
            print(f"  Scheduled for: {scheduled_time.strftime('%A, %d/%m/%Y %H:%M')}")
            print(f"  Timezone: America/Sao_Paulo")
            
            response = input("\nProceed with scheduling? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("[YouTube] Scheduling cancelled")
                return 0
        
        try:
            result = manager.upload_video(video_path, metadata_path, scheduled_time)
            print(f"\n[YouTube] Scheduling successful!")
            print(f"  Video ID: {result['video_id']}")
            print(f"  URL: {result['youtube_url']}")
            print(f"  Scheduled for: {scheduled_time.strftime('%A, %d/%m/%Y %H:%M %Z')}")
            return 0
        except Exception as e:
            print(f"[YouTube] Scheduling failed: {e}")
            return 1
    
    elif args.command == 'schedule-list':
        scheduled = manager.list_scheduled_videos()
        if not scheduled:
            print("[YouTube] No scheduled videos found")
            return 0
        
        print("[YouTube] Scheduled Videos:")
        print("-" * 80)
        for entry in scheduled:
            scheduled_time = datetime.fromisoformat(entry['scheduled_at']) if entry.get('scheduled_at') else None
            time_str = scheduled_time.strftime('%A, %d/%m/%Y %H:%M') if scheduled_time else 'Unknown'
            print(f"Title: {entry['title']}")
            print(f"Video ID: {entry['video_id']}")
            print(f"Scheduled for: {time_str}")
            print(f"URL: {entry['youtube_url']}")
            print("-" * 80)
        return 0
    
    elif args.command == 'schedule-cancel':
        if not args.yes:
            response = input(f"Are you sure you want to cancel scheduled publication for video {args.video_id}? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("[YouTube] Cancel operation cancelled")
                return 0
        
        success = manager.cancel_scheduled_video(args.video_id)
        if success:
            print(f"[YouTube] Successfully cancelled scheduled publication for {args.video_id}")
            return 0
        else:
            print(f"[YouTube] Failed to cancel scheduled publication for {args.video_id}")
            return 1
    
    elif args.command == 'publish-now':
        if not args.yes:
            response = input(f"Are you sure you want to publish video {args.video_id} immediately? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("[YouTube] Publish now operation cancelled")
                return 0
        
        success = manager.publish_now(args.video_id)
        if success:
            print(f"[YouTube] Successfully published video {args.video_id} immediately")
            return 0
        else:
            print(f"[YouTube] Failed to publish video {args.video_id} immediately")
            return 1

    elif args.command == 'schedule-existing':
        scheduled_time = natural_language_to_datetime(args.when)
        if not scheduled_time:
            print(f"[YouTube] Could not parse time expression: '{args.when}'")
            print("Please use formats like:")
            print("  'terça às 6AM'")
            print("  'amanhã às 19h'")
            print("  'segunda-feira'")
            return 1

        if not args.yes:
            response = input(
                f"Schedule video {args.video_id} for {scheduled_time.strftime('%A, %d/%m/%Y %H:%M')}? (y/N): "
            )
            if response.lower() not in ['y', 'yes']:
                print("[YouTube] Schedule operation cancelled")
                return 0

        success = manager.schedule_existing_publish(args.video_id, scheduled_time)
        if success:
            print(f"[YouTube] Successfully scheduled video {args.video_id}")
            return 0
        else:
            print(f"[YouTube] Failed to schedule video {args.video_id}")
            return 1

    elif args.command == 'analytics':
        # Placeholder for analytics implementation
        print("[YouTube] Analytics feature coming soon...")
        print("This will show:")
        print(f"  - Views, likes, comments over last {args.days} days")
        print("  - Top performing videos")
        print("  - Audience demographics")
        print("  - Traffic sources")
        return 0
    
    else:
        parser.print_help()
        return 1

if __name__ == '__main__':
    sys.exit(main())