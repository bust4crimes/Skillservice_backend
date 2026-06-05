from fastapi import APIRouter, HTTPException
from typing import List
from .. import models, schemas

router = APIRouter(prefix="/reviews", tags=["Rating & Service Reviews Subsystem"])

@router.post("/create", response_model=schemas.ReviewResponse)
async def submit_provider_review(review: schemas.ReviewCreate, reviewer_id: str):
    if reviewer_id == review.target_user_id:
        raise HTTPException(status_code=400, detail="Self-evaluations are blocked. You cannot review your own listing profiles.")

    # 1. Verify target user exists
    target_user = await models.User.get(review.target_user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="The target user account could not be resolved.")

    # 2. Insert standard transaction record into MongoDB review storage
    new_review = models.Review(
        rating=review.rating,
        comment=review.comment,
        tag=review.tag,
        target_user_id=review.target_user_id,
        reviewer_id=reviewer_id
    )
    await new_review.insert()

    # 3. Automatically inject skill rating breakdown
    skill_found = False
    for skill in target_user.skills:
        if skill.name.lower() == review.tag.lower():
            new_sub_rating = models.SkillRating(
                reviewer_id=reviewer_id,
                rating=review.rating,
                comment=review.comment
            )
            if not hasattr(skill, 'ratings') or skill.ratings is None:
                skill.ratings = []
            skill.ratings.append(new_sub_rating)
            skill_found = True
            break

    if not skill_found:
        new_sub_rating = models.SkillRating(
            reviewer_id=reviewer_id,
            rating=review.rating,
            comment=review.comment
        )
        on_the_fly_skill = models.UserSkill(
            name=review.tag,
            ratings=[new_sub_rating]
        )
        target_user.skills.append(on_the_fly_skill)

    await target_user.save()

    # 🔥 Blueprint: Trigger Notification for the target user
    reviewer = await models.User.get(reviewer_id)
    reviewer_name = f"{reviewer.first_name} {reviewer.last_name}" if reviewer else "A user"
    
    await models.Notification(
        user_id=review.target_user_id,
        sender_id=reviewer_id,
        sender_name=reviewer_name,
        type="Review",
        message=f"{reviewer_name} left you a {review.rating}-star review: '{review.comment[:20]}...'"
    ).insert()

    return new_review

@router.get("/target/{user_id}", response_model=List[schemas.ReviewResponse])
async def get_all_reviews_for_user(user_id: str):
    user_reviews = await models.Review.find(models.Review.target_user_id == user_id).to_list()
    return user_reviews