#!/usr/bin/env python3
"""
Analyze videos from history.json for engagement metrics.
"""

import sys
import os
import json

# Add the youtube-growth skill directory to the path so we can import it
sys.path.append(os.path.join(os.path.dirname(__file__)))

from youtube_growth import YouTubeGrowthManager, HISTORY_FILE

def analyze_history_videos():
    """Analyze videos stored in history.json for engagement metrics."""
    print("[Analysis] Loading video history...")
    
    # Initialize the manager
    manager = YouTubeGrowthManager()
    
    # Authenticate
    if not manager.authenticate():
        print("[Analysis] Error: Authentication failed")
        return
    
    if not manager.youtube_service:
        print("[Analysis] Error: Could not initialize YouTube service")
        return
    
    print("[Analysis] Authentication successful")
    
    # Load history
    try:
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    except FileNotFoundError:
        print(f"[Analysis] History file not found: {HISTORY_FILE}")
        return
    except json.JSONDecodeError as e:
        print(f"[Analysis] Error parsing history file: {e}")
        return
    
    if not history:
        print("[Analysis] No videos found in history")
        return
    
    print(f"[Analysis] Found {len(history)} videos in history")
    
    # Get statistics for each video
    videos_with_stats = []
    
    for history_key, video_info in history.items():
        youtube_video_id = video_info.get('video_id')
        if not youtube_video_id:
            print(f"[Analysis] Warning: No video_id found for history key {history_key}")
            continue
            
        print(f"[Analysis] Fetching stats for video {youtube_video_id} (from history key {history_key})...")
        
        try:
            # Get video statistics and snippet in one call
            response = manager.youtube_service.videos().list(
                part='snippet,statistics',
                id=youtube_video_id
            ).execute()
            
            if response.get('items'):
                item = response['items'][0]
                stats = item.get('statistics', {})
                snippet = item.get('snippet', {})
                
                # Extract statistics (note: some might be missing if video is private/deleted)
                views = int(stats.get('viewCount', 0))
                likes = int(stats.get('likeCount', 0))
                # Note: dislikeCount is no longer publicly meaningful as of late 2021
                comments = int(stats.get('commentCount', 0))
                
                video_data = {
                    'video_id': youtube_video_id,
                    'title': snippet.get('title', 'Unknown Title'),
                    'views': views,
                    'likes': likes,
                    'comments': comments,
                    'uploaded_at': snippet.get('publishedAt'),
                }
                
                # Calculate engagement rates if views > 0
                if views > 0:
                    video_data['like_rate'] = (likes / views) * 100
                    video_data['comment_rate'] = (comments / views) * 100
                    video_data['engagement_rate'] = video_data['like_rate'] + video_data['comment_rate']
                else:
                    video_data['like_rate'] = 0
                    video_data['comment_rate'] = 0
                    video_data['engagement_rate'] = 0
                
                videos_with_stats.append(video_data)
                print(f"[Analysis] Got stats for {youtube_video_id}: {views} views, {likes} likes, {comments} comments")
            else:
                print(f"[Analysis] No data found for video {youtube_video_id}")
                
        except Exception as e:
            print(f"[Analysis] Error fetching stats for video {youtube_video_id}: {e}")
            import traceback
            traceback.print_exc()
    
    if not videos_with_stats:
        print("[Analysis] No video statistics could be retrieved")
        return
    
    # Analyze the data
    print(f"\n=== ENGAGEMENT ANALYSIS FOR {len(videos_with_stats)} VIDEOS ===")
    
    # Sort by views
    videos_by_views = sorted(videos_with_stats, key=lambda x: x.get('views', 0), reverse=True)
    
    print("\n📊 VIDEOS BY VIEW COUNT:")
    for i, video in enumerate(videos_by_views):
        print(f"  {i+1}. {video['title']}")
        print(f"     ID: {video['video_id']}")
        print(f"     Views: {video['views']:,}")
        print(f"     Likes: {video['likes']:,} ({video.get('like_rate', 0):.2f}%)")
        print(f"     Comments: {video['comments']:,} ({video.get('comment_rate', 0):.2f}%)")
        print(f"     Engagement Rate: {video.get('engagement_rate', 0):.2f}%")
        print()
    
    # Calculate averages
    total_views = sum(v.get('views', 0) for v in videos_with_stats)
    avg_like_rate = sum(v.get('like_rate', 0) for v in videos_with_stats) / len(videos_with_stats) if videos_with_stats else 0
    avg_comment_rate = sum(v.get('comment_rate', 0) for v in videos_with_stats) / len(videos_with_stats) if videos_with_stats else 0
    avg_engagement_rate = avg_like_rate + avg_comment_rate
    
    print(f"📈 AVERAGE METRICS:")
    print(f"   - Average like rate: {avg_like_rate:.2f}%")
    print(f"   - Average comment rate: {avg_comment_rate:.2f}%")
    print(f"   - Average engagement rate: {avg_engagement_rate:.2f}%")
    print()
    
    # Provide recommendations
    print("🎯 RECOMMENDATIONS BASED ON YOUR VIDEOS:")
    print()
    
    if avg_engagement_rate < 2:
        print("🔴 ENGAGEMENT RATE NEEDS IMPROVEMENT")
        print("   • Your average engagement rate is below 2%")
        print("   • Try adding stronger calls-to-action in your videos")
        print("   • Ask specific questions to encourage comments")
        print("   • Respond to every comment to build community")
        print()
    else:
        print("🟢 ENGAGEMENT RATE IS SOLID")
        print("   • Continue encouraging engagement in your videos")
        print()
    
    # Check for top performers
    if len(videos_with_stats) >= 2:
        top_video = max(videos_with_stats, key=lambda x: x.get('engagement_rate', 0))
        print(f"🏆 YOUR TOP PERFORMING VIDEO BY ENGAGEMENT:")
        print(f"   • '{top_video['title']}'")
        print(f"   • Engagement rate: {top_video.get('engagement_rate', 0):.2f}%")
        print(f"   • {top_video['views']:,} views, {top_video['likes']:,} likes, {top_video['comments']:,} comments")
        print()
        print("   💡 ANALYZE THIS VIDEO TO SEE WHAT WORKED:")
        print("      • What was the topic/format?")
        print("      • How long was the video?")
        print("      • What was the thumbnail like?")
        print("      • Did you ask a specific question or make a strong CTA?")
        print()
    
    print("📋 ACTIONABLE STEPS TO IMPROVE ENGAGEMENT:")
    print("   1. In your next video, explicitly ask viewers to like and comment")
    print("   2. Pose a question at the end: 'What's your biggest challenge with [topic]? Comment below!'")
    print("   3. Respond to every comment within the first 2-4 hours of posting")
    print("   4. Use cards or end screens to promote your other videos")
    print("   5. Create curiosity-gap titles that make people want to click")
    print("   6. Use bold, readable text in your thumbnails")
    print("   7. Keep your introductions under 15 seconds to hook viewers quickly")

if __name__ == "__main__":
    analyze_history_videos()
