from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schemas import PostCreate, PostResponse, PostUpdate, PaginatedPostsResponse

from auth import CurrentUser

from config import settings

router = APIRouter()

# Get Posts
@router.get("", response_model=PaginatedPostsResponse)
async def get_posts(
    db: Annotated[AsyncSession, Depends(get_db)], 
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = settings.posts_per_page):

    # Get posts - count query
    count_result = await db.execute(select(func.count()).select_from(models.Post))
    total = count_result.scalar() or 0

    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .order_by(models.Post.date_posted.desc())
        .offset(skip)
        .limit(limit)
    )
    posts = result.scalars().all()

    # Check if there are more posts available to fetch (True or False)
    has_more = skip + len(posts) < total
    
    return PaginatedPostsResponse(
        posts=[PostResponse.model_validate(post) for post in posts],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more
    )

# Create Post
@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate, 
    current_user: CurrentUser, 
    db: Annotated[AsyncSession, Depends(get_db)]):
    
    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=current_user.id
    )

    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names=["author"])

    return new_post   # Post Response

# Get Post
@router.get("/{post_id}", response_model=PostResponse)   # path parameter
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    results = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.id == post_id))
    post = results.scalars().first()

    if post:
        return post

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found!")

# Update Post Full
@router.put("/{post_id}", response_model=PostResponse)   # path parameter
async def update_post_full(
    post_id: int,
    post_data: PostCreate,   # will contain data from request body when updating post
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]):
    results = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = results.scalars().first()

    # Check if the post exists
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found!")

    # Prevent users from updating posts they don't own
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this post!")

    post.title = post_data.title
    post.content = post_data.content

    await db.commit()
    await db.refresh(post, attribute_names=["author"])

    return post

# Update Post Partial
@router.patch("/{post_id}", response_model=PostResponse)   # path parameter
async def update_post_partial(
    post_id: int,
    post_data: PostUpdate,   # will contain data from request body when updating post
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]):
    results = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = results.scalars().first()

    # Checks if the post exists
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found!")

    # Prevent users from updating posts they don't own
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this post!")

    # Pydantic method '(exclude_unset=True)' that converts a model into a dictionary, excluding fields that the client did not provide.
    update_data = post_data.model_dump(exclude_unset=True)

    # Update only the fields provided in the request
    for field, value in update_data.items():
        setattr(post, field, value)   # post.title = "..." and post.content = "..."

    await db.commit()
    await db.refresh(post, attribute_names=["author"])

    return post

# Delete Post
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)   # path parameter
async def delete_post(post_id: int, 
                    current_user: CurrentUser, 
                    db: Annotated[AsyncSession, Depends(get_db)]):
    results = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = results.scalars().first()

    # Checks if the post exists
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found!")

    # Prevent users from updating posts they don't own
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this post!")

    await db.delete(post)
    await db.commit()