from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from collections import namedtuple
import uuid

app = FastAPI(title="จอดไหมจ้ะ (Jord-Maiz-Ja) : ระบบบริหารที่จอดรถ")

class SystemClock:
    def __init__(self):
        self.__current_time = datetime(2026, 3, 10, 8, 0)

    def now(self) -> datetime:
        return self.__current_time

    def set_time(self, date_str: str, time_str: str) -> str:
        """รับ date: dd-mm-yyyy และ time: hh-mm"""
        try:
            day, month, year = map(int, date_str.split("-"))
            hour, minute = map(int, time_str.split("-"))
            self.__current_time = datetime(year, month, day, hour, minute)
            return f"Clock set to: {self.__current_time.strftime('%d-%m-%Y %H:%M')}"
        except Exception:
            return "Error: Invalid format. Use date=dd-mm-yyyy, time=hh-mm"

    def get_time(self) -> str:
        return self.__current_time.strftime("%d-%m-%Y %H:%M")

clock = SystemClock()

class Point:
    def __init__(self, amount: int):
        self.__amount = amount
        self.__expire_time = clock.now() + timedelta(days=365)

    @property
    def amount(self) -> int: return self.__amount
    @amount.setter
    def amount(self, value: int): self.__amount = value

    @property
    def expire_time(self) -> SystemClock: return self.__expire_time

RewardPromo = namedtuple("RewardPromo", ["points_required", "promo_code"])

class Promotion:
    def __init__(self, promoCode: str, amount: float, is_flat: bool = False):
        self.__promoCode = promoCode
        self.__amount = amount
        self.__is_flat = is_flat
        self.__expire = clock.now() + timedelta(days=30)
        self.__reward_promo_list: List[RewardPromo] = [
            RewardPromo(100, "REDEEM100"),
            RewardPromo(200, "REDEEM200"),
        ]
    @property
    def reward_promo_list(self) -> List[RewardPromo]: return self.__reward_promo_list
    @property
    def promoCode(self) -> str: return self.__promoCode
    @property
    def amount(self) -> float: return self.__amount
    @property
    def expire(self) -> SystemClock: return self.__expire
    @property
    def is_flat(self) -> bool: return self.__is_flat

    def calculateDiscount(self, base: float) -> float:
        if self.__is_flat:
            return self.__amount          # ← ลดตรง ๆ เป็นบาท
        return base * (self.__amount / 100)  # ← ลดแบบ %

    def validatePromotion(self, code: str) -> bool:
        return self.__promoCode == code
    
    def get_reward_catalog(self) -> List[RewardPromo]: return self.__reward_promo_list

class Penalty:
    def __init__(self, time: float, reason: str, cash: float):
        self.__time = time
        self.__reason = reason
        self.__cash = cash

    @property
    def time(self) -> float: return self.__time
    @property
    def reason(self) -> str: return self.__reason
    @property
    def cash(self) -> float: return self.__cash

    def calculatePenalty(self, time_hours: float) -> float:
        if time_hours <= 1.0: return self.__cash
        return 0.0
