#!/usr/bin/env python3
"""
Analyze YouTube channel videos for engagement and click-through rate insights.
"""

import sys
import os

# Add the youtube-growth skill directory to the path so we can import it
sys.path.append(os.path.join(os.path.dirname(__file__)))

from youtube_growth import YouTubeGrowthManager
from datetime import datetime, timedelta

def analyze_channel_performance():
    """Analyze channel video performance for engagement and CTR insights."""
    print("[Analysis] Initializing YouTube Analytics...")
    
    # Initialize the manager (this will handle authentication)
    manager = YouTubeGrowthManager()
    
    # Authenticate first
    if not manager.authenticate():
        print("[Analysis] Error: Authentication failed")
        return
    
    if not manager.youtube_service or not manager.analytics_service:
        print("[Analysis] Error: Could not initialize YouTube services")
        return
    
    print("[Analysis] Authentication successful")
    
    # Calculate date range (last 30 days for recent performance)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"[Analysis] Fetching analytics data from {start_date} to {end_date}")
    
    try:
        # YouTube Analytics query for video performance
        # Using 'channel==MINE' to refer to the authenticated user's channel
        response = manager.analytics_service.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='views,likes,comments,shares,estimatedMinutesWatched,averageViewDuration,averageViewPercentage',
            dimensions='video',
            sort='-views',  # Sort by views descending
            maxResults=50   # Get top 50 videos
        ).execute()
        
        if 'rows' not in response or not response['rows']:
            print("[Analysis] No data returned from YouTube Analytics")
            return
        
        # Process the data
        videos = []
        headers = response.get('columnHeaders', [])
        metric_indices = {header['name']: i for i, header in enumerate(headers) if header['columnType'] == 'METRIC'}
        dimension_indices = {header['name']: i for i, header in enumerate(headers) if header['columnType'] == 'DIMENSION'}
        
        for row in response['rows']:
            video_data = {}
            
            # Extract dimensions
            for dim_name, idx in dimension_indices.items():
                video_data[dim_name] = row[idx]
            
            # Extract metrics
            for metric_name, idx in metric_indices.items():
                value = row[idx]
                # Convert numeric values
                if metric_name in ['views', 'likes', 'comments', 'shares']:
                    video_data[metric_name] = int(float(value)) if value else 0
                else:
                    video_data[metric_name] = float(value) if value else 0.0
            
            videos.append(video_data)
        
        print(f"[Analysis] Retrieved data for {len(videos)} videos")
        
        # Analyze the data
        analyze_engagement(videos)
        analyze_retention(videos)
        print_recommendations(videos)
        
    except Exception as e:
        print(f"[Analysis] Error querying YouTube Analytics: {e}")
        import traceback
        traceback.print_exc()

def analyze_engagement(videos):
    """Analyze engagement metrics (likes, comments, shares per view)."""
    print("\n=== ENGAGEMENT ANALYSIS ===")
    
    if not videos:
        print("No video data to analyze")
        return
    
    # Calculate engagement rates for each video
    for video in videos:
        views = video.get('views', 0)
        if views > 0:
            video['like_rate'] = (video.get('likes', 0) / views) * 100
            video['comment_rate'] = (video.get('comments', 0) / views) * 100
            video['share_rate'] = (video.get('shares', 0) / views) * 100
            video['engagement_rate'] = video['like_rate'] + video['comment_rate'] + video['share_rate']
        else:
            video['like_rate'] = 0
            video['comment_rate'] = 0
            video['share_rate'] = 0
            video['engagement_rate'] = 0
    
    # Sort by engagement rate
    videos_by_engagement = sorted(videos, key=lambda x: x.get('engagement_rate', 0), reverse=True)
    
    print(f"Top 5 videos by engagement rate (likes+comments+shares per 100 views):")
    for i, video in enumerate(videos_by_engagement[:5]):
        views = video.get('views', 0)
        like_rate = video.get('like_rate', 0)
        comment_rate = video.get('comment_rate', 0)
        share_rate = video.get('share_rate', 0)
        engagement_rate = video.get('engagement_rate', 0)
        video_id = video.get('video', 'Unknown')
        print(f"  {i+1}. Video {video_id}: {views:,} views")
        print(f"      Likes: {like_rate:.2f}% | Comments: {comment_rate:.2f}% | Shares: {share_rate:.2f}%")
        print(f"      Total Engagement: {engagement_rate:.2f}%")
        print()

def analyze_retention(videos):
    """Analyze audience retention metrics."""
    print("\n=== RETENTION ANALYSIS ===")
    
    if not videos:
        print("No video data to analyze")
        return
    
    # Sort by average view percentage
    videos_by_retention = sorted(videos, key=lambda x: x.get('averageViewPercentage', 0), reverse=True)
    
    print(f"Top 5 videos by average view percentage:")
    for i, video in enumerate(videos_by_retention[:5]):
        views = video.get('views', 0)
        avg_duration = video.get('averageViewDuration', 0)
        avg_percentage = video.get('averageViewPercentage', 0)
        video_id = video.get('video', 'Unknown')
        print(f"  {i+1}. Video {video_id}: {views:,} views")
        print(f"      Average view duration: {avg_duration:.1f} seconds")
        print(f"      Average view percentage: {avg_percentage:.1f}%")
        print()

def print_recommendations(videos):
    """Print specific recommendations based on the analysis."""
    print("\n=== RECOMMENDATIONS FOR IMPROVEMENT ===")
    
    if not videos:
        print("No data available for recommendations")
        return
    
    # Calculate averages for comparison
    total_views = sum(v.get('views', 0) for v in videos)
    avg_like_rate = sum(v.get('like_rate', 0) for v in videos) / len(videos) if videos else 0
    avg_comment_rate = sum(v.get('comment_rate', 0) for v in videos) / len(videos) if videos else 0
    avg_share_rate = sum(v.get('share_rate', 0) for v in videos) / len(videos) if videos else 0
    avg_engagement_rate = avg_like_rate + avg_comment_rate + avg_share_rate
    avg_view_percentage = sum(v.get('averageViewPercentage', 0) for v in videos) / len(videos) if videos else 0
    
    print(f"Channel averages (last 30 days):")
    print(f"  - Like rate: {avg_like_rate:.2f}%")
    print(f"  - Comment rate: {avg_comment_rate:.2f}%")
    print(f"  - Share rate: {avg_share_rate:.2f}%")
    print(f"  - Total engagement rate: {avg_engagement_rate:.2f}%")
    print(f"  - Average view percentage: {avg_view_percentage:.1f}%")
    print()
    
    # Provide specific recommendations
    print("🎯 ACTIONABLE RECOMMENDATIONS:")
    print()
    
    if avg_view_percentage < 50:
        print("🔴 AUDIENCE RETENTION NEEDS IMPROVEMENT")
        print("   • Your average view percentage is below 50%, meaning viewers are dropping off quickly")
        print("   • Focus on improving the first 15-15-30 seconds of your videos (the hook)")
        print("   • Use pattern jumps, visual changes, or narrative twists every 20-30 seconds")
        print("   • Analyze your top-performing videos to see what keeps viewers engaged")
        print()
    else:
        print("🟢 AUDIENCE RETENTION IS GOOD")
        print("   • Your average view percentage is strong - focus on maintaining this")
        print()
    
    if avg_engagement_rate < 2:
        print("🔴 ENGAGEMENT RATE IS LOW")
        print("   • Aim for >2% engagement rate (likes+comments+shares per 100 views)")
        print("   • Add clear calls-to-action: Ask viewers to like, comment, and subscribe")
        print("   • Pose questions in your videos to encourage comments")
        print("   • Respond to comments to build community and encourage more engagement")
        print("   • Consider running comment pinning or highlighting top comments")
        print()
    else:
        print("🟢 ENGAGEMENT RATE IS ACCEPTABLE")
        print("   • Continue what's working to maintain engagement levels")
        print()
    
    # Check for consistency in top performers
    top_5_by_views = sorted(videos, key=lambda x: x.get('views', 0), reverse=True)[:5]
    top_5_by_engagement = sorted(videos, key=lambda x: x.get('engagement_rate', 0), reverse=True)[:5]
    
    top_view_ids = set(v.get('video') for v in top_5_by_views)
    top_engagement_ids = set(v.get('video') for v in top_5_by_engagement)
    overlap = top_view_ids & top_engagement_ids
    
    print(f"📊 CONSISTENCY ANALYSIS:")
    print(f"   • {len(overlap)} of your top 5 viewed videos are also in top 5 by engagement")
    print(f"   • This suggests {'consistent' if len(overlap) >= 3 else 'inconsistent'} quality across your content")
    print()
    
    if len(overlap) < 3:
        print("💡 SUGGESTION: Study your top-performing videos (by both views and engagement)")
        print("   • What do they have in common? Topic, format, length, thumbnail style?")
        print("   • Replicate those elements in future content")
        print()
    
    print("📋 QUICK WINS TO IMPLEMENT TODAY:")
    print("   1. Add a verbal call-to-action in your videos: 'If you found this helpful, please like and subscribe'")
    print("   2. Use end screens to promote your other videos and encourage binge-watching")
    print("   3. Create custom thumbnails with clear, readable text and contrasting colors")
    print("   4. Keep video titles under 60 characters to avoid truncation on mobile")
    print("   5. Post videos when your audience is most active (check YouTube Analytics for timing)")

if __name__ == "__main__":
    analyze_channel_performance()
