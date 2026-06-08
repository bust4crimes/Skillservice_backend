from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from .. import models, schemas

router = APIRouter(prefix="/posts", tags=["News Feed & Search"])

@router.post("/", response_model=schemas.PostResponse)
async def create_post(post: schemas.PostCreate):
    new_post = models.Post(**post.dict())
    await new_post.insert()
    return schemas.PostResponse(
        id=str(new_post.id),
        title=new_post.title,
        description=new_post.description,
        type=new_post.type,
        owner_id=new_post.owner_id,
        media_urls=new_post.media_urls,
        comments=[schemas.CommentResponse(
            id=c.id,
            user_id=c.user_id,
            user_name=c.user_name,
            comment_text=c.comment_text,
            timestamp=c.timestamp,
        ) for c in new_post.comments],
        is_deleted=new_post.is_deleted,
        deleted_at=new_post.deleted_at,
    )

@router.get("/all", response_model=List[schemas.PostResponse])
async def get_all_posts():
    """
    Fetches all active, unarchived, and non-deleted posts to populate the main feed.
    """
    query = {"is_deleted": False, "is_archived": False}
    posts = await models.Post.find(query).to_list()
    return posts

@router.get("/search", response_model=List[schemas.PostResponse])
async def search_posts(
    location: Optional[str] = None,
    post_type: Optional[str] = None,
    keyword: Optional[str] = None
):
    query = {"is_deleted": False, "is_archived": False}
    if post_type: query["type"] = post_type
    
    posts = await models.Post.find(query).to_list()
    if keyword:
        posts = [p for p in posts if keyword.lower() in p.title.lower()]
    return posts

@router.put("/archive/{post_id}")
async def archive_post(post_id: str):
    post = await models.Post.get(post_id)
    if not post: 
        raise HTTPException(status_code=404, detail="Post not found")
    post.is_archived = True
    await post.save()
    return {"message": "Post archived"}

@router.get("/recently-deleted", response_model=List[schemas.PostResponse])
async def get_recently_deleted(user_id: str):
    return await models.Post.find({"owner_id": user_id, "is_deleted": True}).to_list()

@router.put("/restore/{post_id}")
async def restore_post(post_id: str):
    post = await models.Post.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.is_deleted = False
    await post.save()
    return {"message": "Post restored"}