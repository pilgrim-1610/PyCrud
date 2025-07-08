from fastapi.testclient import TestClient
import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app, Base, engine, session_local, User


client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    # Clean up before each test
    db = session_local()
    db.query(User).delete()
    db.commit()
    db.close()
    yield
    # Clean up after each test
    db = session_local()
    db.query(User).delete()
    db.commit()
    db.close()

def test_create_user():
    response = client.post("/users/", json={"name": "Alice", "email": "alice@example.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert "id" in data

def test_read_users():
    # Create two users
    client.post("/users/", json={"name": "Bob", "email": "bob@example.com"})
    client.post("/users/", json={"name": "Carol", "email": "carol@example.com"})
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

def test_read_user_by_id():
    # Create a user
    res = client.post("/users/", json={"name": "Dave", "email": "dave@example.com"})
    user_id = res.json()["id"]
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["name"] == "Dave"

def test_read_user_by_id_not_found():
    response = client.get("/users/99999")
    assert response.status_code == 404
    assert response.json() == {"detail":"User not found"}

def test_update_user():
    res = client.post("/users/", json={"name": "Eve", "email": "eve@example.com"})
    user_id = res.json()["id"]
    response = client.put(f"/users/{user_id}", json={"name": "Eve Updated"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Eve Updated"
    assert data["email"] == "eve@example.com"

def test_update_user_not_found():
    response = client.put("/users/99999", json={"name": "Ghost"})
    assert response.status_code == 404
    assert response.json() == {"detail":"User not found"}

def test_delete_user():
    res = client.post("/users/", json={"name": "Frank", "email": "frank@example.com"})
    user_id = res.json()["id"]
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    # Confirm user is deleted
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 404
    assert get_response.json() == {"detail":"User not found"}

def test_delete_user_not_found():
    response = client.delete("/users/99999")
    assert response.status_code == 404
    assert response.json() == {"detail":"User not found"}