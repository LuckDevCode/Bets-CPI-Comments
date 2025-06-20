from googleapiclient.discovery import build
from dotenv import load_dotenv
import time, os

load_dotenv()

API_KEY = os.getenv('YOUTUBE_API_KEY')
VIDEO_ID = 'DqXKpxalF8E'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

if not API_KEY:
    print("ERROR: The environment variable YOUTUBE_API_KEY was not defined!")
    exit()

def get_all_video_comments(api_key, video_id):
    all_comments_data = []
    next_page_token = None
    total_comments = 0

    try:
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=api_key)

        page_count = 0
        while True:
            page_count += 1
            print(f"INFO: Fetching comments on page '{page_count}'...")

            request = youtube.commentThreads().list(
                part="snippet, replies",
                videoId=video_id,
                textFormat="plainText",
                maxResults=100,
                pageToken=next_page_token,
                order="time"
            )

            response = request.execute()

            for item in response.get("items", []):
                comment_snippet = item.get("snippet", {})
                top_level_comment = comment_snippet.get("topLevelComment", {})
                actual_comment_snippet = top_level_comment.get("snippet", {})

                comment_text = actual_comment_snippet.get("textDisplay")
                author_name = actual_comment_snippet.get("authorDisplayName")
                publish_date = actual_comment_snippet.get("publishedAt")
                like_count = actual_comment_snippet.get("likeCount")
                comment_id = top_level_comment.get("id")

                all_replies = []
                replies_data = item.get("replies", {}).get("comments", [])
                for reply_item in replies_data:
                    reply_comment_text = reply_item.get("snippet", {}).get("textDisplay")
                    reply_author_name = reply_item.get("snippet", {}).get("authorDisplayName")
                    reply_publish_date = reply_item.get("snippet", {}).get("publishedAt")
                    reply_like_count = reply_item.get("snippet", {}).get("likeCount")
                    reply_comment_id = reply_item.get("snippet", {}).get("id")

                    reply = {
                        "id": reply_comment_id,
                        "author": reply_author_name,
                        "published_at": reply_publish_date,
                        "like_count": reply_like_count,
                        "text": reply_comment_text
                    }

                    total_comments += 1

                    all_replies.append(reply)

                comment_data = {
                    "id": comment_id,
                    "author": author_name,
                    "published_at": publish_date,
                    "like_count": like_count,
                    "text": comment_text,
                    "replies": all_replies
                }

                total_comments += 1

                all_comments_data.append(comment_data)

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                print("INFO: There are no more comment pages.")
                break

            time.sleep(0.1)

        print(f"\n----> Total number of comments collected: {total_comments}.")
        return all_comments_data

    except Exception as e:
        print(f"ERROR: {e}")
        print(f"\n----> Total number of comments collected: {total_comments}.")
        return all_comments_data

if __name__ == '__main__':
    comments = get_all_video_comments(API_KEY, VIDEO_ID)

    if comments:

        with open("comments_cpi.txt", "w", encoding="utf-8") as f:
            for comment_info in comments:
                f.write(f"Author: {comment_info['author']}\n")
                f.write(f"Date: {comment_info['published_at']}\n")
                f.write(f"Likes: {comment_info['like_count']}\n")
                f.write(f"Text: {comment_info['text']}\n")
                f.write(f"Replies:\n")
                if len(comment_info['replies']) > 0:
                    for reply_info in comment_info['replies']:
                        f.write(f"----> Author: {reply_info['author']}\n")
                        f.write(f"----> Date: {reply_info['published_at']}\n")
                        f.write(f"----> Likes: {reply_info['like_count']}\n")
                        f.write(f"----> Text: {reply_info['text']}\n")
                        f.write("-" * 20 + "\n")
                else:
                    f.write("----> This comment has no replies\n")
                    f.write("-" * 20 + "\n")
        print("\nINFO: Comments saved to 'comments_cpi.txt'")