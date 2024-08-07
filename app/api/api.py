from fastapi import APIRouter
from app.api.endpoints import customer, account, transfer

api_router = APIRouter()
api_router.include_router(customer.router, prefix="/customers", tags=["customers"])
api_router.include_router(account.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(transfer.router, prefix="/transfers", tags=["transfers"])