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
    
class Parking_Slot:
    def __init__(self, slot_id: str):
        self.__slot_id = slot_id
        self.__slot_status = "AVAILABLE"
        self.__time_list = []

    @property
    def slot_id(self) -> str: return self.__slot_id
    @property
    def slot_status(self) -> str: return self.__slot_status
    @property
    def time_list(self) -> list: return self.__time_list

    def calculateTime(self, time_in: datetime) -> float:
        delta = clock.now() - time_in
        hours = delta.total_seconds() / 3600
        return round(hours, 2)

    def set_status(self, status: str):
        self.__slot_status = status

    # ใน Parking_Slot — คำนวณค่าจอด Normal
    def calculateParkingFee(self, time_in: datetime, bonus_hours: int = 0) -> float:
        hours = self.calculateTime(time_in)
        free_hours = 2 + bonus_hours  # ฟรี 2 ชม. + โบนัสจากแสตมป์
        billable = max(0, hours - free_hours)
        if billable <= 0:
            return 0.0
        fee = 0.0
        # ชม. 3-4 (billable ชม. 1-2) → 20 บาท/ชม.
        tier1 = min(billable, 2)
        fee += tier1 * 20
        # ชม. 5+ (billable ชม. 3+) → 50 บาท/ชม.
        tier2 = max(0, billable - 2)
        fee += tier2 * 50
        return round(fee, 2)


class Normal_Slot(Parking_Slot): pass


class EV_Slot(Parking_Slot):
    def __init__(self, slot_id: str, station: Charging_Station):
        super().__init__(slot_id)
        self.__Charging_station = station
        self.__charge_done_time: Optional[datetime] = None  # ✅ เพิ่ม

    @property
    def charge_done_time(self) -> Optional[datetime]: return self.__charge_done_time
    @charge_done_time.setter
    def charge_done_time(self, value: datetime): self.__charge_done_time = value
    @property
    def Charging_station(self) -> Charging_Station: return self.__Charging_station

    def checkAvaliable(self) -> bool:
        return self.slot_status == "AVAILABLE"

    def setStatus(self, status: str):
        self.set_status(status)
    
    # ใน EV_Slot — เพิ่ม Idle Fee
    def calculateIdleFee(self, charge_done_time: datetime) -> float:
        idle_minutes = (clock.now() - charge_done_time).total_seconds() / 60
        billable_minutes = max(0, idle_minutes - 15)
        return round(billable_minutes * 20, 2)


class Restricted_Slot(Parking_Slot):
    def check_role(self, car: Cars) -> bool:
        raise NotImplementedError
class Super_Car_Slot(Restricted_Slot):
    def check_role(self, car: Cars) -> bool:
        return isinstance(car, Super_Car)
class Disable_Person_Slot(Restricted_Slot):
    def check_role(self, car: Cars) -> bool:
        return isinstance(car, Normal_Car)


class Floor:
    def __init__(self, floor_status: str):
        self.__parking_slot_list: List[Parking_Slot] = []
        self.__floor_status = floor_status

    @property
    def parking_slot_list(self) -> List[Parking_Slot]: return self.__parking_slot_list
    @property
    def floor_status(self) -> str: return self.__floor_status

    def addSlot(self, slot: Parking_Slot):
        self.__parking_slot_list.append(slot)

    def checkSlot(self):
        return [
            f"slot_id={s.slot_id} | type={type(s).__name__} | status={s.slot_status}"
            for s in self.__parking_slot_list
            if s.slot_status == "AVAILABLE"
        ]


class Parking_Lot:
    def __init__(self, lot_id: str):
        self.__parking_lot_id = lot_id
        self.__floor_list: List[Floor] = []
        self.__admin_log = []

    @property
    def parking_lot_id(self) -> str: return self.__parking_lot_id
    @property
    def floor_list(self) -> List[Floor]: return self.__floor_list
    @property
    def admin_log(self) -> list: return self.__admin_log

    def find_available_slot(self, slot_id: str) -> Optional[Parking_Slot]:
        for fl in self.__floor_list:
            for s in fl.parking_slot_list:
                if s.slot_id == slot_id and s.slot_status == "AVAILABLE":
                    return s
        return None

    def find_available_ev_slot(self, slot_id: str) -> Optional[EV_Slot]:
        for fl in self.__floor_list:
            for s in fl.parking_slot_list:
                if isinstance(s, EV_Slot) and s.slot_id == slot_id and s.slot_status == "AVAILABLE":
                    return s
        return None

    def addFloor(self, floor: Floor):
        self.__floor_list.append(floor)


class Parking_Slot_Time:
    def __init__(self, slot: Parking_Slot, time_in: datetime, time_out: Optional[datetime] = None):
        self.__Parking_slot = slot
        self.__time_in = time_in
        self.__time_out = time_out

    @property
    def Parking_slot(self) -> Parking_Slot: return self.__Parking_slot
    @property
    def time_in(self) -> datetime: return self.__time_in
    @property
    def time_out(self) -> Optional[datetime]: return self.__time_out
    @time_out.setter
    def time_out(self, value: datetime): self.__time_out = value

class Partner_Shop:
    def __init__(self, shop_id: str, shop_name: str, location: str):
        self.__shop_id = shop_id
        self.__shop_name = shop_name
        self.__location = location
        self.__my_promotion: List[Promotion] = []
        self.__validation_history: List[str] = []

    @property
    def shop_id(self) -> str: return self.__shop_id
    @property
    def shop_name(self) -> str: return self.__shop_name
    @property
    def location(self) -> str: return self.__location
    @property
    def my_promotion(self) -> List[Promotion]: return self.__my_promotion

    def check_shop_id(self, sid: str) -> bool:
        return self.__shop_id == sid

    def log_validation(self, member_name: str, points: int):
        self.__validation_history.append(
            f"member={member_name} | points={points} | time={clock.now().strftime('%Y-%m-%d %H:%M')}"
        )

    def view_validation_history(self) -> List[str]:
        return self.__validation_history if self.__validation_history else ["No history"]

    def create_promotion(self, amount: float) -> int:
        return int(amount // 100)