from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from services.config import config

router = APIRouter()


class AccountInfo(BaseModel):
    account_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    active: bool = True


class AccountCreate(BaseModel):
    session_key: str
    name: Optional[str] = None
    email: Optional[str] = None


@router.get("")
async def list_accounts():
    """List all configured accounts"""
    accounts = []
    for acc in config.accounts:
        accounts.append({
            "account_id": acc.get("account_id", "unknown"),
            "name": acc.get("name"),
            "email": acc.get("email"),
            "active": acc.get("active", True)
        })
    return {"accounts": accounts}


@router.post("")
async def add_account(account: AccountCreate):
    """Add a new account"""
    acc_dict = {
        "session_key": account.session_key,
        "name": account.name,
        "email": account.email,
        "active": True,
        "account_id": f"acc_{len(config.accounts) + 1}"
    }
    config.accounts.append(acc_dict)
    config.save()
    return {"message": "Account added", "account_id": acc_dict["account_id"]}


@router.delete("/{account_id}")
async def remove_account(account_id: str):
    """Remove an account"""
    for i, acc in enumerate(config.accounts):
        if acc.get("account_id") == account_id:
            config.accounts.pop(i)
            config.save()
            return {"message": "Account removed"}
    raise HTTPException(status_code=404, detail="Account not found")


@router.post("/{account_id}/activate")
async def activate_account(account_id: str):
    """Activate an account"""
    for acc in config.accounts:
        if acc.get("account_id") == account_id:
            acc["active"] = True
            config.save()
            return {"message": "Account activated"}
    raise HTTPException(status_code=404, detail="Account not found")


@router.post("/{account_id}/deactivate")
async def deactivate_account(account_id: str):
    """Deactivate an account"""
    for acc in config.accounts:
        if acc.get("account_id") == account_id:
            acc["active"] = False
            config.save()
            return {"message": "Account deactivated"}
    raise HTTPException(status_code=404, detail="Account not found")


@router.post("/{account_id}/toggle")
async def toggle_account(account_id: str):
    """Toggle account active status"""
    for acc in config.accounts:
        if acc.get("account_id") == account_id:
            acc["active"] = not acc.get("active", True)
            config.save()
            return {"message": "Account toggled", "active": acc["active"]}
    raise HTTPException(status_code=404, detail="Account not found")