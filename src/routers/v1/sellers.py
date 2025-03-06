from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload

from src.models.sellers import Seller
from src.schemas.sellers import SellerCreate, SellerOut, SellerOutBooks
from src.configurations import get_async_session

seller_router = APIRouter(tags=["sellers"], prefix="/seller")


@seller_router.post(
    "/",
    response_model=SellerOut,
    status_code=status.HTTP_201_CREATED
)
async def create_seller(
    seller: SellerCreate,
    session: AsyncSession = Depends(get_async_session)
):

    new_seller = Seller(
        first_name=seller.first_name,
        last_name=seller.last_name,
        e_mail=seller.e_mail,
        password=seller.password,
    )

    session.add(new_seller)
    await session.commit()

    return new_seller


@seller_router.get("/", response_model=list[SellerOutBooks])
async def get_sellers(session: AsyncSession = Depends(get_async_session)):
    query = select(Seller).options(selectinload(Seller.books))
    result = await session.execute(query)
    sellers = result.scalars().all()
    return sellers


@seller_router.get("/{seller_id}", response_model=SellerOutBooks)
async def get_seller(
    seller_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    query = select(Seller).options(joinedload(Seller.books)).filter(
        Seller.id == seller_id
    )
    result = await session.execute(query)
    seller = result.scalars().first()

    if seller is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Продавец не найден."
        )
    return seller


@seller_router.put("/{seller_id}", response_model=SellerOut)
async def update_seller(
    seller_id: int,
    seller: SellerCreate,
    session: AsyncSession = Depends(get_async_session)
):
    query = select(Seller).filter(Seller.id == seller_id)
    result = await session.execute(query)
    existing_seller = result.scalar_one_or_none()
    if existing_seller is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Продавец не найден."
        )

    existing_seller.first_name = seller.first_name
    existing_seller.last_name = seller.last_name
    existing_seller.e_mail = seller.e_mail
    existing_seller.password = seller.password

    await session.commit()
    return existing_seller


@seller_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(
    seller_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    query = select(Seller).filter(Seller.id == seller_id)
    result = await session.execute(query)
    seller = result.scalar_one_or_none()
    if seller is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Продавец не найден."
        )

    await session.delete(seller)
    await session.commit()
    return {"detail": "Запись успешно удалена."}
