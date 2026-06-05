import requests

BASE_URL = "http://127.0.0.1:8000"


def assert_status(response, expected_status):
    if response.status_code != expected_status:
        raise AssertionError(
            f"Expected {expected_status}, got {response.status_code}: {response.text}"
        )
    return response.json()


def test():
    response = requests.get(f"{BASE_URL}/")
    print(f"Server Status: {assert_status(response, 200)}")

    user = assert_status(
        requests.post(
            f"{BASE_URL}/users/",
            json={
                "name": "Kim Soon",
                "location": "Manila",
                "bio": "Frontend developer",
                "is_available": True,
            },
        ),
        201,
    )
    reviewer = assert_status(
        requests.post(
            f"{BASE_URL}/users/",
            json={
                "name": "Alex Reyes",
                "location": "Quezon City",
                "bio": "Project client",
                "is_available": True,
            },
        ),
        201,
    )
    print(f"Created users: {user['id']}, {reviewer['id']}")

    updated_user = assert_status(
        requests.put(f"{BASE_URL}/users/{user['id']}", json={"bio": "Full-stack developer"}),
        200,
    )
    print(f"Updated user bio: {updated_user['bio']}")

    post = assert_status(
        requests.post(
            f"{BASE_URL}/posts/",
            json={
                "title": "Build a portfolio website",
                "description": "Need a responsive site for a student portfolio.",
                "type": "Job",
                "owner_id": user["id"],
            },
        ),
        201,
    )
    print(f"Created post: {post['id']}")

    updated_post = assert_status(
        requests.put(f"{BASE_URL}/posts/{post['id']}", json={"type": "Service"}),
        200,
    )
    print(f"Updated post type: {updated_post['type']}")

    review = assert_status(
        requests.post(
            f"{BASE_URL}/reviews/",
            json={
                "rating": 5,
                "comment": "Great communication and fast delivery.",
                "tag": "Reliable",
                "target_user_id": user["id"],
                "reviewer_id": reviewer["id"],
            },
        ),
        201,
    )
    print(f"Created review: {review['id']}")

    reviews = assert_status(requests.get(f"{BASE_URL}/reviews/user/{user['id']}"), 200)
    print(f"Reviews for user: {len(reviews)}")

    assert_status(requests.delete(f"{BASE_URL}/reviews/{review['id']}"), 200)
    assert_status(requests.delete(f"{BASE_URL}/posts/{post['id']}?user_id={user['id']}"), 200)
    assert_status(requests.delete(f"{BASE_URL}/users/{reviewer['id']}"), 200)
    assert_status(requests.delete(f"{BASE_URL}/users/{user['id']}"), 200)
    print("CRUD test completed successfully.")

if __name__ == "__main__":
    test()
