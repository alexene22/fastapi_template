from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from typing import List, Optional
import uvicorn


app = FastAPI(
    title="DevOps Reddit API",
    description="A FastAPI application to fetch top posts from r/devops",
    version="1.0.0"
)


class RedditPost(BaseModel):
    title: str
    author: str
    score: int
    num_comments: int
    url: str
    created_utc: float
    permalink: str
    selftext: Optional[str] = None


class RedditResponse(BaseModel):
    posts: List[RedditPost]
    total_count: int


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to the DevOps Reddit API",
        "endpoints": {
            "/devops/top": "Get top 10 posts from r/devops",
            "/docs": "API documentation"
        }
    }


@app.get("/devops/top", response_model=RedditResponse)
async def get_top_devops_posts(limit: int = 10):
    """
    Fetch top posts from r/devops subreddit
    
    Args:
        limit: Number of posts to retrieve (max 25, default 10)
    
    Returns:
        RedditResponse: List of top posts with metadata
    """
    if limit > 25:
        raise HTTPException(status_code=400, detail="Limit cannot exceed 25")
    
    reddit_url = f"https://www.reddit.com/r/devops/top.json?limit={limit}"
    
    try:
        async with httpx.AsyncClient() as client:
            # Reddit requires a User-Agent header
            headers = {
                "User-Agent": "FastAPI-DevOps-Tutorial/1.0"
            }
            response = await client.get(reddit_url, headers=headers, timeout=10.0)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract posts from Reddit's JSON structure
            posts = []
            for item in data['data']['children']:
                post_data = item['data']
                post = RedditPost(
                    title=post_data['title'],
                    author=post_data['author'],
                    score=post_data['score'],
                    num_comments=post_data['num_comments'],
                    url=post_data['url'],
                    created_utc=post_data['created_utc'],
                    permalink=f"https://reddit.com{post_data['permalink']}",
                    selftext=post_data.get('selftext', '')[:500] if post_data.get('selftext') else None
                )
                posts.append(post)
            
            return RedditResponse(
                posts=posts,
                total_count=len(posts)
            )
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Reddit API error: {e.response.text}"
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Reddit API request timed out"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
