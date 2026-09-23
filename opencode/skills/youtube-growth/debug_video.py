#!/usr/bin/env python3
"""
Debug video statistics fetching.
"""

import sys
import os

# Add the youtube-growth skill directory to the path so we can import it
sys.path.append(os.path.join(os.path.dirname(__file__)))

from youtube_growth import YouTubeGrowthManager

def debug_video_fetch():
    """Debug fetching video statistics."""
    print("[Debug] Initializing...")
    
    # Initialize the manager
    manager = YouTubeGrowthManager()
    
    # Authenticate
    if not manager.authenticate():
        print("[Debug] Error: Authentication failed")
        return
    
    if not manager.youtube_service:
        print("[Debug] Error: Could not initialize YouTube service")
        return
    
    print("[Debug] Authentication successful")
    
    # Test with one video ID from history
    video_id = "Y_jyk5zRybs"
    print(f"[Debug] Fetching stats for video {video_id}...")
    
    try:
        # Get video statistics and snippet in one call
        response = manager.youtube_service.videos().list(
            part='snippet,statistics',
            id=video_id
        ).execute()
        
        print(f"[Debug] Full response: {response}")
        
        if response.get('items'):
            print(f"[Debug] Found {len(response['items'])} items")
            item = response['items'][0]
            print(f"[Debug] Item keys: {item.keys()}")
            stats = item.get('statistics', {})
            snippet = item.get('snippet', {})
            print(f"[Debug] Statistics: {stats}")
            print(f"[Debug] Snippet title: {snippet.get('title')}")
        else:
            print(f"[Debug] No items in response")
            print(f"[Debug] Response keys: {response.keys()}")
            
    except Exception as e:
        print(f"[Debug] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_video_fetch()
