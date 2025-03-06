import pytest
from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.books import Book
from src.models.sellers import Seller


@pytest.mark.asyncio
async def test_create_seller(db_session, async_client):
    new_seller_data = {
        "first_name": "Alex",
        "last_name": "Smith",
        "e_mail": "alex.smith@example.com",
        "password": "securepassword"
    }

    response = await async_client.post("/api/v1/seller/", json=new_seller_data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()
    assert "id" in result_data
    assert result_data["first_name"] == new_seller_data["first_name"]
    assert result_data["last_name"] == new_seller_data["last_name"]
    assert result_data["e_mail"] == new_seller_data["e_mail"]

    saved_seller = await db_session.get(Seller, result_data["id"])
    assert saved_seller is not None
    assert saved_seller.first_name == new_seller_data["first_name"]
    assert saved_seller.last_name == new_seller_data["last_name"]
    assert saved_seller.e_mail == new_seller_data["e_mail"]
    assert saved_seller.password == new_seller_data["password"]


@pytest.mark.asyncio
async def test_get_seller_with_books(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivan@example.com",
        password="securepassword"
    )
    book_1 = Book(
        title="Clean Architecture",
        author="Robert Martin",
        year=2025,
        pages=300,
        seller=seller
    )
    book_2 = Book(
        title="The Pragmatic Programmer",
        author="Dave Thomas",
        year=2020,
        pages=250,
        seller=seller
    )

    db_session.add_all([seller, book_1, book_2])
    await db_session.flush()

    result = await db_session.execute(
        select(Seller)
        .options(selectinload(Seller.books))
        .filter(Seller.id == seller.id)
    )

    seller_with_books = result.scalars().first()

    assert seller_with_books is not None
    assert len(seller_with_books.books) == 2
    assert seller_with_books.books[0].title == "Clean Architecture"
    assert seller_with_books.books[1].title == "The Pragmatic Programmer"

    response = await async_client.get(f"/api/v1/seller/{seller.id}")

    assert response.status_code == 200

    result_data = response.json()
    assert result_data["first_name"] == seller.first_name
    assert result_data["last_name"] == seller.last_name
    assert len(result_data["books"]) == 2
    assert result_data["books"][0]["title"] == book_1.title
    assert result_data["books"][1]["title"] == book_2.title


@pytest.mark.asyncio
async def test_get_all_sellers_with_books(db_session, async_client):

    seller_1 = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivan8@example.com",
        password="password"
    )
    book_1 = Book(
        title="Clean Architecture",
        author="Robert Martin",
        year=2025,
        pages=300,
        seller=seller_1
    )

    seller_2 = Seller(
        first_name="Jane",
        last_name="Doe",
        e_mail="jane.doe@example.com",
        password="password")
    book_2 = Book(
        title="The Pragmatic Programmer",
        author="Dave Thomas",
        year=2020,
        pages=250,
        seller=seller_2
    )

    db_session.add_all([seller_1, seller_2, book_1, book_2])
    await db_session.commit()

    response = await async_client.get("/api/v1/seller/")

    assert response.status_code == 200
    sellers_data = response.json()

    assert len(sellers_data) == 2
    assert "books" in sellers_data[0]
    assert len(sellers_data[0]["books"]) == 1
    assert sellers_data[0]["books"][0]["title"] == "Clean Architecture"

    assert "books" in sellers_data[1]
    assert len(sellers_data[1]["books"]) == 1
    assert sellers_data[1]["books"][0]["title"] == "The Pragmatic Programmer"


@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivan9@example.com",
        password="securepassword"
    )
    db_session.add(seller)
    await db_session.flush()

    updated_data = {
        "first_name": "Vanya",
        "last_name": "Ivanov",
        "e_mail": "vanya@example.com",
        "password": "newpassword"
    }

    response = await async_client.put(
        f"/api/v1/seller/{seller.id}",
        json=updated_data
    )

    assert response.status_code == status.HTTP_200_OK

    updated_seller = await db_session.get(Seller, seller.id)

    assert updated_seller.first_name == "Vanya"
    assert updated_seller.last_name == "Ivanov"
    assert updated_seller.e_mail == "vanya@example.com"
    assert updated_seller.password == "newpassword"


@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivan10@example.com",
        password="securepassword"
    )
    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/seller/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    deleted_seller = await db_session.get(Seller, seller.id)
    assert deleted_seller is None


@pytest.mark.asyncio
async def test_delete_non_existent_seller(db_session, async_client):
    response = await async_client.delete("/api/v1/seller/999999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
