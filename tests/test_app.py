from copy import deepcopy

import pytest


def test_root_redirects_to_homepage(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client, activity_data):
    expected = deepcopy(activity_data)

    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == expected
    assert response.json()["Chess Club"] == {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    }


def test_signup_adds_participant(client, activity_data):
    email = "new.student@mergington.edu"
    expected = deepcopy(activity_data)
    expected["Chess Club"]["participants"].append(email)

    response = client.post(
        "/activities/Chess Club/signup", params={"email": email}
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Chess Club"
    }
    listing = client.get("/activities")
    assert listing.status_code == 200
    assert listing.json() == expected


def test_unregister_removes_participant(client, activity_data):
    email = "michael@mergington.edu"
    expected = deepcopy(activity_data)
    expected["Chess Club"]["participants"].remove(email)

    response = client.delete(
        "/activities/Chess Club/unregister", params={"email": email}
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from Chess Club"
    }
    listing = client.get("/activities")
    assert listing.status_code == 200
    assert listing.json() == expected


@pytest.mark.parametrize(
    "method, path, email, status_code, detail",
    [
        (
            "POST",
            "/activities/Chess Club/signup",
            "michael@mergington.edu",
            400,
            "Student already signed up for this activity",
        ),
        (
            "POST",
            "/activities/Unknown Club/signup",
            "new.student@mergington.edu",
            404,
            "Activity not found",
        ),
        (
            "DELETE",
            "/activities/Unknown Club/unregister",
            "michael@mergington.edu",
            404,
            "Activity not found",
        ),
        (
            "DELETE",
            "/activities/Chess Club/unregister",
            "new.student@mergington.edu",
            404,
            "Student is not signed up for this activity",
        ),
    ],
)
def test_rejected_mutation_preserves_activities(
    client, activity_data, method, path, email, status_code, detail
):
    expected = deepcopy(activity_data)

    response = client.request(method, path, params={"email": email})

    assert response.status_code == status_code
    assert response.json() == {"detail": detail}
    assert activity_data == expected
    listing = client.get("/activities")
    assert listing.status_code == 200
    assert listing.json() == expected


@pytest.mark.parametrize(
    "method, path",
    [
        ("POST", "/activities/Chess Club/signup"),
        ("DELETE", "/activities/Chess Club/unregister"),
    ],
)
def test_missing_email_returns_validation_error(
    client, activity_data, method, path
):
    expected = deepcopy(activity_data)

    response = client.request(method, path)

    assert response.status_code == 422
    assert any(
        error["loc"] == ["query", "email"]
        for error in response.json()["detail"]
    )
    assert activity_data == expected
