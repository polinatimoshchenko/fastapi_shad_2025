import pytest
from sqlalchemy import select
from fastapi import status
from icecream import ic

from src.models.sellers import Seller
from src.models.books import Book


# Тест на ручку создающую книгу
@pytest.mark.asyncio
async def test_create_book(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivan1@example.com",
        password="securepassword"
    )

    db_session.add(seller)
    await db_session.flush()

    assert seller.id is not None

    # Передаем seller_id при создании книги
    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "pages": 300,
        "year": 2025,
        "seller_id": seller.id
    }

    # Отправляем запрос для создания книги
    response = await async_client.post("/api/v1/books/", json=data)

    # Проверка статуса ответа
    assert response.status_code == status.HTTP_201_CREATED

    # Получаем данные книги из ответа
    result_data = response.json()

    # Проверяем, что id книги возвращен
    resp_book_id = result_data.pop("id", None)
    assert resp_book_id, "Book id not returned from endpoint"

    # Проверяем, что данные книги правильные
    assert result_data == {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "pages": 300,
        "year": 2025,
    }


@pytest.mark.asyncio
async def test_create_book_with_old_year(async_client):
    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "pages": 300,
        "year": 1986,  # Год, который не проходит валидацию
    }
    response = await async_client.post("/api/v1/books/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# Тест на ручку получения списка книг
@pytest.mark.asyncio
async def test_get_books(db_session, async_client):
    # Создаем продавца
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivan1@example.com",
        password="securepassword"
    )
    db_session.add(seller)
    await db_session.flush()

    # Создаем книги вручную, добавляя seller_id
    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages=104, seller_id=seller.id)
    book_2 = Book(author="Lermontov", title="Mziri", year=1997, pages=104, seller_id=seller.id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/books/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["books"]) == 2

    # Проверяем интерфейс ответа
    assert response.json() == {
        "books": [
            {
                "title": "Eugeny Onegin",
                "author": "Pushkin",
                "year": 2001,
                "id": book.id,
                "pages": 104,
            },
            {
                "title": "Mziri",
                "author": "Lermontov",
                "year": 1997,
                "id": book_2.id,
                "pages": 104,
            },
        ]
    }


# Тест на ручку получения одной книги
@pytest.mark.asyncio
async def test_get_single_book(db_session, async_client):
    # Создаем продавца
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivan2@example.com",
        password="securepassword"
    )
    db_session.add(seller)
    await db_session.flush()

    # Создаем книги вручную с seller_id
    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages=104, seller_id=seller.id)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.get(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа
    assert response.json() == {
        "title": "Eugeny Onegin",
        "author": "Pushkin",
        "year": 2001,
        "pages": 104,
        "id": book.id,
    }


# Тест на ручку обновления книги
@pytest.mark.asyncio
async def test_update_book(db_session, async_client):
    # Создаем продавца
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivan3@example.com",
        password="securepassword"
    )
    db_session.add(seller)
    await db_session.flush()

    # Создаем книгу с seller_id
    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages=104, seller_id=seller.id)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/books/{book.id}",
        json={
            "title": "Mziri",
            "author": "Lermontov",
            "pages": 100,
            "year": 2007,
            "id": book.id,
            "seller_id": seller.id,  # Добавляем seller_id
        },
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(Book, book.id)
    assert res.title == "Mziri"
    assert res.author == "Lermontov"
    assert res.pages == 100
    assert res.year == 2007
    assert res.id == book.id


@pytest.mark.asyncio
async def test_delete_book(db_session, async_client):
    # Создаем продавца
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivan4@example.com",
        password="securepassword"
    )
    db_session.add(seller)
    await db_session.flush()

    # Создаем книгу с seller_id
    book = Book(author="Lermontov", title="Mtziri", pages=510, year=2024, seller_id=seller.id)
    db_session.add(book)
    await db_session.flush()
    ic(book.id)

    response = await async_client.delete(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.commit()  # Коммит изменений

    all_books = await db_session.execute(select(Book))
    res = all_books.scalars().all()

    assert len(res) == 0


@pytest.mark.asyncio
async def test_delete_book_with_invalid_book_id(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivan5@example.com",
        password="securepassword"
    )
    db_session.add(seller)
    await db_session.flush()

    # Создаем книгу с seller_id
    book = Book(author="Lermontov", title="Mtziri", pages=510, year=2024, seller_id=seller.id)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/books/{book.id + 1}")  # Неверный ID

    assert response.status_code == status.HTTP_404_NOT_FOUND
