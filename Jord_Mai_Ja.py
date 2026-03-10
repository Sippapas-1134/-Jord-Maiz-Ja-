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

class Payment_Gateway(ABC):
    def __init__(self, account_number: str):
        self.__account_number = account_number

    @property
    def account_number(self) -> str: return self.__account_number

    @abstractmethod
    def paying(self, amount: float) -> bool:
        pass


class QR_Code(Payment_Gateway):
    def __init__(self, account_number: str):
        super().__init__(account_number)
        self.__account_list: List[str] = ["13245678", "87654321"]
    
    @property
    def account_list(self) -> List[str]:
        return self.__account_list

    def paying(self, amount: float) -> bool:
        acc = self.account_number
        if not acc.isdigit() or len(acc) != 8:
            return False
        if acc not in self.__account_list:
            return False
        return True


class Credit_Card(Payment_Gateway):
    def __init__(self, card_number: str):
        super().__init__(card_number)
        self.__credit_list: List[str] = ["123456", "654321"]

    @property
    def credit_list(self) -> List[str]:
        return self.__credit_list

    def paying(self, amount: float) -> bool:
        card = self.account_number
        if not card.isdigit() or len(card) != 6:
            return False
        if card not in self.__credit_list:
            return False
        return True
    
class Cars:
    def __init__(self, license: str, color: str, brand: str):
        self.__license = license
        self.__color = color
        self.__brand = brand

    @property
    def license(self) -> str: return self.__license
    @property
    def color(self) -> str: return self.__color
    @property
    def brand(self) -> str: return self.__brand

    def __str__(self): return f"{self.__license} ({self.__brand})"


class Normal_Car(Cars): pass
class Super_Car(Cars): pass


class EV_Car(Cars):
    def __init__(self, license: str, color: str, brand: str):
        super().__init__(license, color, brand)
        self.__isCharging = False
        self.__current_battery = 100.0

    @property
    def isCharging(self) -> bool: return self.__isCharging
    @isCharging.setter
    def isCharging(self, value: bool): self.__isCharging = value

    @property
    def current_battery(self) -> float: return self.__current_battery
    @current_battery.setter
    def current_battery(self, value: float): self.__current_battery = value


class Charging_Station:
    def __init__(self, station_id: str, capacity: float):
        self.__charging_station_id = station_id
        self.__capacity = capacity
        self.__status = "Idle"

    @property
    def charging_station_id(self) -> str: return self.__charging_station_id
    @property
    def capacity(self) -> float: return self.__capacity
    @property
    def status(self) -> str: return self.__status
    @status.setter
    def status(self, value: str): self.__status = value

    def calculateChargingFee(self, kwh: float) -> float:
        return kwh * 7.5