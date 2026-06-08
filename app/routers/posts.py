from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from .. import models, schemas

router = APIRouter(prefix="/posts", tags=["News Feed & Search"])

def _post_to_response(p: models.Post) -> schemas.PostResponse:
    return schemas.PostResponse(
        id=str(p.id),
        title=p.title,
        description=p.description,
        type=p.type,
        owner_id=p.owner_id,
        media_urls=p.media_urls,
        comments=[schemas.CommentResponse(
            id=c.id, user_id=c.user_id, user_name=c.user_name,
            comment_text=c.comment_text, timestamp=c.timestamp,
        ) for c in p.comments],
        is_deleted=p.is_deleted,
        deleted_at=p.deleted_at,
        timestamp=p.timestamp.isoformat() if p.timestamp else None,
    )

@router.post("/", response_model=schemas.PostResponse)
async def create_post(post: schemas.PostCreate):
    new_post = models.Post(**post.dict())
    await new_post.insert()
    return _post_to_response(new_post)

@router.get("/all", response_model=List[schemas.PostResponse])
async def get_all_posts():
    query = {"is_deleted": False, "is_archived": False}
    posts = await models.Post.find(query).to_list()
    return [_post_to_response(p) for p in posts]

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
    return [_post_to_response(p) for p in posts]

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
    posts = await models.Post.find({"owner_id": user_id, "is_deleted": True}).to_list()
    return [_post_to_response(p) for p in posts]

@router.put("/restore/{post_id}")
async def restore_post(post_id: str):
    post = await models.Post.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.is_deleted = False
    await post.save()
    return {"message": "Post restored"}