from fastapi import FastAPI, HTTPException
from fastmcp import FastMCP
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from collections import namedtuple
import uuid

mcp = FastMCP("Demo 🚀")
app = FastAPI(title="จอดไหมจ้ะ (Jord-Maiz-Ja) : ระบบบริหารที่จอดรถ")

# System Clock (เอาไว้จำลองเวลา)
class SystemClock:
    def __init__(self):
        self.__current_time = datetime(2026, 3, 10, 8, 0)

    def now(self) -> datetime:
        return self.__current_time

    def set_time(self, date_str: str, time_str: str) -> str:
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
    def expire_time(self) -> datetime: return self.__expire_time

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
    def expire(self) -> datetime: return self.__expire
    @property
    def is_flat(self) -> bool: return self.__is_flat

    def calculateDiscount(self, base: float) -> float:
        if self.__is_flat:
            return self.__amount
        return base * (self.__amount / 100)

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

        if abs(time_hours) <= 1.0: return self.__cash
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
    def account_list(self) -> List[str]: return self.__account_list

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
    def credit_list(self) -> List[str]: return self.__credit_list

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

    def calculateParkingFee(self, time_in: datetime, bonus_hours: int = 0) -> float:
        hours = self.calculateTime(time_in)
        free_hours = 2 + bonus_hours
        billable = max(0, hours - free_hours)
        if billable <= 0:
            return 0.0
        fee = 0.0
        tier1 = min(billable, 2)
        fee += tier1 * 20
        tier2 = max(0, billable - 2)
        fee += tier2 * 50
        return round(fee, 2)


class Normal_Slot(Parking_Slot): pass


class EV_Slot(Parking_Slot):
    def __init__(self, slot_id: str, station: Charging_Station):
        super().__init__(slot_id)
        self.__Charging_station = station
        self.__charge_done_time: Optional[datetime] = None

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
        self.__actual_entry_time: Optional[datetime] = None   
        self.__actual_exit_time: Optional[datetime] = None   

    @property
    def Parking_slot(self) -> Parking_Slot: return self.__Parking_slot

    @property
    def time_in(self) -> datetime: return self.__time_in

    @property
    def time_out(self) -> Optional[datetime]: return self.__time_out
    @time_out.setter
    def time_out(self, value: datetime): self.__time_out = value

    @property
    def actual_entry_time(self) -> Optional[datetime]: return self.__actual_entry_time
    @actual_entry_time.setter
    def actual_entry_time(self, value: datetime): self.__actual_entry_time = value

    @property
    def actual_exit_time(self) -> Optional[datetime]: return self.__actual_exit_time
    @actual_exit_time.setter
    def actual_exit_time(self, value: datetime): self.__actual_exit_time = value

    @property
    def billing_entry_time(self) -> datetime:
        return self.__actual_entry_time if self.__actual_entry_time else self.__time_in

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

class User:
    def __init__(self, id: str, name: str, tele_num: str):
        self.__id = id
        self.__name = name
        self.__tele_num = tele_num
        self.__car: List[Cars] = []
        self.__role = "General"
        self.__user_status = "Active"
        self.__reservation_list: List['Reservation'] = []
        self.__transaction_list: List['Transaction'] = []

    @property
    def id(self) -> str: return self.__id

    @property
    def name(self) -> str: return self.__name
    @name.setter
    def name(self, value: str): self.__name = value

    @property
    def tele_num(self) -> str: return self.__tele_num
    @tele_num.setter
    def tele_num(self, value: str): self.__tele_num = value

    @property
    def car(self) -> List[Cars]: return self.__car

    @property
    def role(self) -> str: return self.__role
    @role.setter
    def role(self, value: str): self.__role = value

    @property
    def user_status(self) -> str: return self.__user_status
    @user_status.setter
    def user_status(self, value: str): self.__user_status = value

    @property
    def reservation_list(self) -> List['Reservation']: return self.__reservation_list

    @property
    def transaction_list(self) -> List['Transaction']: return self.__transaction_list

    def view_transaction_history(self) -> List[str]:
        return [t.get_info() for t in self.__transaction_list]

    def view_reservation_history(self) -> List[str]:
        return [
            f"res_id={r.reservation_id} | license={r.Car.license} | slot={r.Parking_slot_time.Parking_slot.slot_id}"
            f" | time_in={r.Parking_slot_time.time_in.strftime('%Y-%m-%d %H:%M')}"
            f" | actual_entry={r.Parking_slot_time.actual_entry_time.strftime('%Y-%m-%d %H:%M') if r.Parking_slot_time.actual_entry_time else 'Not checked in'}"
            f" | actual_exit={r.Parking_slot_time.actual_exit_time.strftime('%Y-%m-%d %H:%M') if r.Parking_slot_time.actual_exit_time else 'Not checked out'}"
            f" | status={r.reservation_status} | amount={r.amount}"
            for r in self.__reservation_list
        ]

    def add_car_to_user(self, lic: str, col: str, br: str, c_type: str, all_users: List['User']) -> str:
        for u in all_users:
            for c in u.car:
                if c.license == lic: return "Error: License duplicated"
        if len(self.__car) >= 2: return "Error: Limit 2 cars per user"
        if not (lic[0:2].isalpha() and lic[2:].isdigit() and len(lic) == 6):
            return "Error: License format invalid"
        if c_type.upper() == "EV":
            new_car = EV_Car(lic, col, br)
        elif c_type.upper() == "NORMAL":
            new_car = Normal_Car(lic, col, br)
        elif c_type.upper() == "SUPER":
            new_car = Super_Car(lic, col, br)
        else:
            return "Error: Invalid car type"
        self.__car.append(new_car)
        return f"Add car success | license={new_car.license} | color={new_car.color} | brand={new_car.brand} | type={c_type.upper()}"

    def remove_car_from_user(self, lic: str) -> str:
        for c in self.__car:
            if c.license == lic:
                self.__car.remove(c)
                return "Remove car success"
        return "Error: Car not found"

    def edit_info(self, name: Optional[str], tele_num: Optional[str]) -> str:
        if name: self.__name = name
        if tele_num: self.__tele_num = tele_num
        return f"User info updated | name={self.__name} | telephone={self.__tele_num}"


class Member(User):
    def __init__(self, u: User):
        super().__init__(u.id, u.name, u.tele_num)
        for c in u.car:
            self.car.append(c)
        for t in u.transaction_list:
            self.transaction_list.append(t)
        self.role = "Member"
        self.__point: List[Point] = []
        self.__expiry_date = clock.now() + timedelta(days=30)
        self.__collected_promotion: List[Promotion] = [Promotion("DISC20", 20)]

    @property
    def point(self) -> List[Point]: return self.__point

    @property
    def expiry_date(self) -> datetime: return self.__expiry_date

    @property
    def collected_promotion(self) -> List[Promotion]: return self.__collected_promotion

    def earn_point(self, p: Point):
        self.__point.append(p)

    def is_expired(self) -> bool:
        return clock.now() > self.__expiry_date

    def renew_membership(self):
        self.__expiry_date = clock.now() + timedelta(days=30)

    def check_member_id(self, mid: str) -> bool:
        return self.id == mid

    def view_point_transactions(self) -> List[str]:
        return [
            f"amount={p.amount} | expire={p.expire_time.strftime('%Y-%m-%d')}"
            for p in self.__point
        ]

    def add_promotion(self, promo: Promotion) -> str:
        for p in self.__collected_promotion:
            if p.promoCode == promo.promoCode:
                return "Error: Promotion already collected"
        self.__collected_promotion.append(promo)
        return f"Promotion {promo.promoCode} added"

    def check_promotions(self) -> List[str]:
        return [
            f"code={p.promoCode} | discount={p.amount} | expire={p.expire.strftime('%Y-%m-%d')}"
            for p in self.__collected_promotion
        ]

    def redeem_reward(self, points_to_redeem: int) -> str:
        promo_ref = Promotion("", 0)
        tier = next((r for r in promo_ref.reward_promo_list
                     if r.points_required == points_to_redeem), None)
        if not tier:
            return "Error: Invalid points amount. Use 100 or 200"
        total_points = sum(p.amount for p in self.__point)
        if total_points < points_to_redeem:
            return f"Error: Not enough points (have {total_points}, need {points_to_redeem})"
        remaining = points_to_redeem
        new_point_list = []
        for p in self.__point:
            if remaining <= 0:
                new_point_list.append(p)
            elif p.amount <= remaining:
                remaining -= p.amount
            else:
                p.amount -= remaining
                remaining = 0
                new_point_list.append(p)
        self.__point = new_point_list
        new_promo = Promotion(tier.promo_code, 100.0, is_flat=True)
        self.__collected_promotion.append(new_promo)
        return f"redeemed={points_to_redeem} | promo_code={tier.promo_code} | points_remaining={sum(p.amount for p in self.__point)}"

class Payment:
    def __init__(self, res: 'Reservation', method: str):
        self.__Reservation = res
        self.__payment_method = method
        self.__payment_status = "Pending"
        self.__total_amount = 0.0
        self.__discount = 0.0

    @property
    def Reservation(self) -> 'Reservation': return self.__Reservation
    @property
    def payment_method(self) -> str: return self.__payment_method
    @property
    def payment_status(self) -> str: return self.__payment_status
    @payment_status.setter
    def payment_status(self, value: str): self.__payment_status = value

    @property
    def total_amount(self) -> float: return self.__total_amount
    @total_amount.setter
    def total_amount(self, value: float): self.__total_amount = value

    @property
    def discount(self) -> float: return self.__discount

    def use_promotion(self, promo: Promotion, base: float):
        self.__discount = promo.calculateDiscount(base)

    def calculateTotal(self, base: float) -> float:
        self.__total_amount = base - self.__discount
        return self.__total_amount

    def processPayment(self, gateway: Payment_Gateway) -> bool:
        return gateway.paying(self.__total_amount)


class Transaction:
    def __init__(self, user: User, payment: Optional[Payment] = None,
                 trans_type: str = "payment", points: int = 0, shop_name: str = ""):
        self.__User = user
        self.__Payment = payment
        self.__trans_type = trans_type
        self.__points = points
        self.__shop_name = shop_name
        self.__payment_time = clock.now()
        self.__trans_id = f"TX-{uuid.uuid4().hex[:6].upper()}"

    @property
    def User(self) -> User: return self.__User
    @property
    def Payment(self) -> Optional[Payment]: return self.__Payment
    @property
    def payment_time(self) -> datetime: return self.__payment_time
    @property
    def trans_id(self) -> str: return self.__trans_id

    def get_info(self) -> str:
        if self.__trans_type == "earn":
            return (f"trans_id={self.__trans_id} | type=earn"
                    f" | points={self.__points} | shop={self.__shop_name}"
                    f" | time={self.__payment_time.strftime('%Y-%m-%d %H:%M')}")
        return (f"trans_id={self.__trans_id} | type=payment"
                f" | amount={self.__Payment.total_amount} | method={self.__Payment.payment_method}"
                f" | time={self.__payment_time.strftime('%Y-%m-%d %H:%M')}")


class Reservation:
    def __init__(self, res_id: str, user: User, car: Cars, lot: Parking_Lot, slot_time: Parking_Slot_Time):
        self.__reservation_id = res_id
        self.__User = user
        self.__Car = car
        self.__Parking_lot = lot
        self.__Parking_slot_time = slot_time
        self.__reservation_status = "Pending"
        self.__amount = 0.0

    @property
    def reservation_id(self) -> str: return self.__reservation_id
    @property
    def User(self) -> User: return self.__User
    @property
    def Car(self) -> Cars: return self.__Car
    @property
    def Parking_lot(self) -> Parking_Lot: return self.__Parking_lot
    @property
    def Parking_slot_time(self) -> Parking_Slot_Time: return self.__Parking_slot_time

    @property
    def reservation_status(self) -> str: return self.__reservation_status
    @reservation_status.setter
    def reservation_status(self, value: str): self.__reservation_status = value

    @property
    def amount(self) -> float: return self.__amount
    @amount.setter
    def amount(self, value: float): self.__amount = value

    def sumTotal(self, charging_fee: float = 0.0, parking_fee: float = 0.0, idle_fee: float = 0.0) -> float:
        self.__amount = parking_fee + charging_fee + idle_fee
        return self.__amount

    def cancel(self, time_hours: float, penalty_sys: Penalty, gateway: Payment_Gateway) -> bool:
        pen_amt = penalty_sys.calculatePenalty(time_hours)
        if pen_amt > 0:
            pay = Payment(self, "QR")
            pay.total_amount = pen_amt
            if not pay.processPayment(gateway):
                return False
        self.__Parking_slot_time.Parking_slot.set_status("AVAILABLE")
        self.__reservation_status = "Cancelled"
        return True

    def findReservation(self, rid: str) -> bool:
        return self.__reservation_id == rid

    def checkin(self) -> str:
        if self.__reservation_status == "Cancelled":
            return "Error: Reservation is cancelled"
        if self.__reservation_status == "PAID":
            return "Error: Reservation already paid"
        if self.__reservation_status == "CheckedIn":
            return "Error: Already checked in"
        if self.__reservation_status == "CheckedOut":
            return "Error: Already checked out, please proceed to payment"

        self.__Parking_slot_time.actual_entry_time = clock.now()
        self.__Parking_slot_time.Parking_slot.set_status("OCCUPIED")
        self.__reservation_status = "CheckedIn"
        return (
            f"Check-in success | res_id={self.__reservation_id}"
            f" | slot={self.__Parking_slot_time.Parking_slot.slot_id}"
            f" | actual_entry={self.__Parking_slot_time.actual_entry_time.strftime('%Y-%m-%d %H:%M')}"
        )
    
    def checkout(self) -> str:
        if self.__reservation_status != "CheckedIn":
            return f"Error: Must be checked in before checking out (current status: {self.__reservation_status})"

        self.__Parking_slot_time.actual_exit_time = clock.now()
        self.__reservation_status = "CheckedOut"

        slot = self.__Parking_slot_time.Parking_slot
        entry = self.__Parking_slot_time.actual_entry_time

        if isinstance(slot, EV_Slot):
            parking_fee = 0.0
            idle_fee = slot.calculateIdleFee(slot.charge_done_time) if slot.charge_done_time else 0.0
            estimated_total = self.__amount + idle_fee
        else:
            parking_fee = slot.calculateParkingFee(entry)
            idle_fee = 0.0
            estimated_total = parking_fee

        return (
            f"Check-out success | res_id={self.__reservation_id}"
            f" | actual_exit={self.__Parking_slot_time.actual_exit_time.strftime('%Y-%m-%d %H:%M')}"
            f" | parking_fee={parking_fee} | idle_fee={idle_fee}"
            f" | estimated_total={estimated_total}"
            f" | status=CheckedOut (please proceed to payment)"
        )

class Jord_System:
    def __init__(self):
        self.__User_list: List[User] = []
        self.__Reservation_list: List[Reservation] = []
        self.__Partner_shop_list: List[Partner_Shop] = []

        self.__Parking_lot = Parking_Lot("LOT_01")
        fl = Floor("Open")
        for i in range(1, 15):
            station = Charging_Station(f"CS{i}", 50.0)
            fl.addSlot(EV_Slot(f"EV{i}", station))
            fl.addSlot(Normal_Slot(f"N{i}"))
            fl.addSlot(Super_Car_Slot(f"SC{i}"))
        self.__Parking_lot.addFloor(fl)

    @property
    def User_list(self) -> List[User]: return self.__User_list
    @property
    def Reservation_list(self) -> List[Reservation]: return self.__Reservation_list
    @property
    def Partner_shop_list(self) -> List[Partner_Shop]: return self.__Partner_shop_list
    @property
    def Parking_lot(self) -> Parking_Lot: return self.__Parking_lot

    def check_user_id(self, uid: str) -> Optional[User]:
        for u in self.__User_list:
            if u.id == uid: return u
        return None

    def checkin(self, uid: str, res_id: str) -> str:
        user = self.check_user_id(uid)
        if not user: return "Error: User not found"
        res = next((r for r in self.__Reservation_list if r.findReservation(res_id)), None)
        if not res: return "Error: Reservation not found"
        if res.User.id != uid: return "Error: Unauthorized"
        return res.checkin()
    
    def checkout(self, uid: str, res_id: str) -> str:
        user = self.check_user_id(uid)
        if not user: return "Error: User not found"
        res = next((r for r in self.__Reservation_list if r.findReservation(res_id)), None)
        if not res: return "Error: Reservation not found"
        if res.User.id != uid: return "Error: Unauthorized"
        return res.checkout()

    def cancel_reservation(self, uid: str, res_id: str, pay_method: str, acc: Optional[str] = None, card_no: Optional[str] = None) -> str:
        user = self.check_user_id(uid)
        if not user: return "Error: User not found"
        res = next((r for r in self.__Reservation_list if r.findReservation(res_id)), None)
        if not res: return "Error: Reservation not found"
        if res.reservation_status == "PAID": return "Error: Already paid, cannot cancel"
        if res.reservation_status == "Cancelled": return "Error: Already cancelled"
        if res.reservation_status == "CheckedIn": return "Error: Already checked in, cannot cancel"
        if res.User.id != uid: return "Error: Unauthorized"

        if pay_method.upper() == "QR":
            if not acc: return "Error: Missing account number (acc)"
            gw = QR_Code(acc)
        elif pay_method.upper() == "CREDIT":
            if not card_no: return "Error: Missing card number (card_no)"
            gw = Credit_Card(card_no)
        else:
            return "Error: Invalid payment method"

        time_diff = abs((res.Parking_slot_time.time_in - clock.now()).total_seconds() / 3600)
        pen = Penalty(1.0, "Late cancel", 100.0)
        if res.cancel(time_diff, pen, gw):
            return "Reservation cancelled successfully"
        return "Error: Cancel failed (Invalid account format or penalty payment failed)"

    def add_point_from_shop(self, uid: str, shop_id: str, amount: float) -> str:
        shop = next((s for s in self.__Partner_shop_list if s.check_shop_id(shop_id)), None)
        if not shop: return "Error: Shop not found"
        if amount <= 0: return "Error: Invalid amount"
        user = self.check_user_id(uid)
        if not isinstance(user, Member): return "Error: Not a Member"
        pts_amount = shop.create_promotion(amount)
        if pts_amount <= 0: return "Error: Invalid amount (minimum 100 baht per point)"
        user.earn_point(Point(pts_amount))
        tx = Transaction(user, trans_type="earn", points=pts_amount, shop_name=shop.shop_name)
        user.transaction_list.append(tx)
        shop.log_validation(user.name, pts_amount)
        return f"Added {pts_amount} points to Member {user.name}, New total points: {sum(p.amount for p in user.point)}"

    def add_car(self, uid: str, lic: str, col: str, br: str, c_type: str) -> str:
        user = self.check_user_id(uid)
        if not user: return "Error: User not found"
        return user.add_car_to_user(lic, col, br, c_type, self.__User_list)

    def remove_car(self, uid: str, lic: str) -> str:
        user = self.check_user_id(uid)
        if not user: return "Error: User not found"
        for res in self.__Reservation_list:
            if res.Car.license == lic and res.reservation_status in ["Pending", "CheckedIn", "CheckedOut"]:
                return "Error: Car has active reservation"
        return user.remove_car_from_user(lic)

    def view_shop_validation_history(self, shop_id: str) -> List[str]:
        shop = next((s for s in self.__Partner_shop_list if s.check_shop_id(shop_id)), None)
        if not shop: return ["Error: Shop not found"]
        return shop.view_validation_history()

    def edit_user_info(self, uid: str, name: Optional[str], tele_num: Optional[str]) -> str:
        user = self.check_user_id(uid)
        if not user: return "Error: User not found"
        return user.edit_info(name, tele_num)

    def view_point_transactions(self, uid: str):
        user = self.check_user_id(uid)
        if not user: return "Error: User not found"
        if not isinstance(user, Member): return "Error: Not a Member"
        return user.view_point_transactions()

    def add_promotion_to_member(self, uid: str, shop_id: str, promo_code: str) -> str:
        shop = next((s for s in self.__Partner_shop_list if s.check_shop_id(shop_id)), None)
        if not shop: return "Error: Shop not found"
        user = self.check_user_id(uid)
        if not isinstance(user, Member): return "Error: Not a Member"
        valid_tiers = Promotion("", 0).reward_promo_list
        tier = next((r for r in valid_tiers if r.promo_code == promo_code), None)
        if not tier:
            return f"Error: Invalid promo_code. Allowed: {[r.promo_code for r in valid_tiers]}"
        return user.add_promotion(Promotion(promo_code, tier.points_required, is_flat=True))

    def check_promotions(self, uid: str):
        user = self.check_user_id(uid)
        if not user: return "Error: User not found"
        if not isinstance(user, Member): return "Error: Not a Member"
        return user.check_promotions()

    def redeem_reward(self, uid: str, points_to_redeem: int) -> str:
        user = self.check_user_id(uid)
        if not user: return "Error: User not found"
        if not isinstance(user, Member): return "Error: Not a Member"
        return user.redeem_reward(points_to_redeem)

    def upgrade_to_member(self, uid: str, pay_method: str, acc: Optional[str] = None, card_no: Optional[str] = None) -> str:
        for i, u in enumerate(self.__User_list):
            if u.id == uid:
                has_qr_data     = bool(acc)
                has_credit_data = bool(card_no)
                if has_qr_data and has_credit_data:
                    return "Error: Cannot provide both QR and Credit Card info"
                if isinstance(u, Member): return "Error: Already Member"
                if pay_method.upper() == "QR":
                    if has_credit_data: return "Error: QR method selected, but Credit Card info provided"
                    if not acc: return "Error: Missing account number (acc)"
                    method = QR_Code(acc)
                    pay = Payment(None, "QR")
                elif pay_method.upper() == "CREDIT":
                    if has_qr_data: return "Error: Credit method selected, but QR info provided"
                    if not card_no: return "Error: Missing card number (card_no)"
                    method = Credit_Card(card_no)
                    pay = Payment(None, "CREDIT")
                else:
                    return "Error: Invalid payment method"
                pay.total_amount = 300.0
                if not pay.processPayment(method):
                    return "Error: Payment failed (Invalid account format)"
                self.__User_list[i] = Member(u)
                return "Upgraded to Member"
        return "Error: User not found"

    def check_available_slots(self) -> List[str]:
        result = []
        for fl in self.__Parking_lot.floor_list:
            result.extend(fl.checkSlot())
        return result

    def renew_membership(self, uid: str, pay_method: str, acc: str) -> str:
        user = self.check_user_id(uid)
        if not user:
            return "Error: User not found"
        elif not isinstance(user, Member):
            return "Error: Not a member"
        if pay_method.upper() == "QR":
            method = QR_Code(acc)
            pay = Payment(None, "QR") 
        elif pay_method.upper() == "CREDIT":
            method = Credit_Card(acc)
            pay = Payment(None, "CREDIT")
        pay.total_amount = 500.0
        if not pay.processPayment(method): return "Error: Payment failed (Invalid account format)"
        user.renew_membership()
        return f"Membership renewed successfully | expiry_date={user.expiry_date.strftime('%Y-%m-%d')}"

    def create_reservation(self, uid: str, lic: str, slot_id: str, target: datetime):
        user = self.check_user_id(uid)
        if not user: return "Error: User not found"
        my_car = next((c for c in user.car if c.license == lic), None)
        if not my_car: return "Error: Car not found"
        target_slot = self.__Parking_lot.find_available_slot(slot_id)
        if not target_slot: return "Error: Slot not available"
        if isinstance(target_slot, Restricted_Slot):
            if not target_slot.check_role(my_car):
                return "Error: Car type not allowed for this slot"
        target_slot.set_status("RESERVED")
        res = Reservation(
            f"RES-{uuid.uuid4().hex[:4].upper()}", user, my_car,
            self.__Parking_lot, Parking_Slot_Time(target_slot, target)
        )
        self.__Reservation_list.append(res)
        user.reservation_list.append(res)
        return f"Reservation created | res_id={res.reservation_id}"

    def create_ev_reservation(self, uid: str, lic: str, slot_id: str, target: datetime, kwh: float):
        user = self.check_user_id(uid)
        if not user: return "Error: User not found"
        my_car = next((c for c in user.car if c.license == lic), None)
        if not my_car: return "Error: Car not found"
        if not isinstance(my_car, EV_Car): return "Error: Car is not an EV"
        ev_slot = self.__Parking_lot.find_available_ev_slot(slot_id)
        if not ev_slot: return "Error: EV Slot not available"
        charging_fee = ev_slot.Charging_station.calculateChargingFee(kwh)
        charge_hours = kwh / ev_slot.Charging_station.capacity
        ev_slot.charge_done_time = target + timedelta(hours=charge_hours)
        ev_slot.set_status("RESERVED")
        ev_slot.Charging_station.status = "In Use"
        res = Reservation(
            f"RES-{uuid.uuid4().hex[:4].upper()}", user, my_car,
            self.__Parking_lot, Parking_Slot_Time(ev_slot, target)
        )
        res.amount = res.sumTotal(charging_fee)
        self.__Reservation_list.append(res)
        user.reservation_list.append(res)
        return f"Reservation created | res_id={res.reservation_id} | slot_id={slot_id} | charging_kwh={kwh} | charging_fee={charging_fee} | total_amount={res.amount}"

    def paying(self, req: 'PayReq'):
        res = next((r for r in self.__Reservation_list if r.reservation_id == req.res_id), None)
        if not res:
            raise HTTPException(status_code=404, detail="Error: Reservation not found")
        if res.reservation_status == "PAID":
            raise HTTPException(status_code=400, detail="Error: Reservation already paid")
        if res.reservation_status == "Cancelled":
            raise HTTPException(status_code=400, detail="Error: Reservation already cancelled")
        if res.reservation_status not in ["CheckedOut", "Pending"]:
            raise HTTPException(status_code=400, detail=f"Error: Cannot pay at this stage (status={res.reservation_status}). Please check out first.")

        promo_code = req.promo_code if req.promo_code and req.promo_code.strip().lower() != "string" else None
        acc        = req.acc        if req.acc        and req.acc.strip().lower()        != "string" else None
        card_no    = req.card_no    if req.card_no    and req.card_no.strip().lower()    != "string" else None

        has_qr_data     = bool(acc)
        has_credit_data = bool(card_no)

        if has_qr_data and has_credit_data:
            raise HTTPException(status_code=400, detail="Error: Cannot provide both QR and Credit Card info.")
        if req.method.upper() == "QR":
            if has_credit_data:
                raise HTTPException(status_code=400, detail="Error: QR method selected, but Credit Card info provided.")
            if not acc:
                raise HTTPException(status_code=400, detail="Error: Missing account number (acc).")
            gw  = QR_Code(acc)
            pay = Payment(res, "QR")
        elif req.method.upper() == "CREDIT":
            if has_qr_data:
                raise HTTPException(status_code=400, detail="Error: Credit method selected, but QR info provided.")
            if not card_no:
                raise HTTPException(status_code=400, detail="Error: Missing card number (card_no).")
            gw  = Credit_Card(card_no)
            pay = Payment(res, "CREDIT")
        else:
            raise HTTPException(status_code=400, detail="Error: Invalid payment method.")

        slot = res.Parking_slot_time.Parking_slot

        billing_entry = res.Parking_slot_time.billing_entry_time

        if isinstance(slot, EV_Slot):
            parking_fee = 0.0
            idle_fee = slot.calculateIdleFee(slot.charge_done_time) if slot.charge_done_time else 0.0
        else:
            parking_fee = slot.calculateParkingFee(billing_entry)
            idle_fee = 0.0

        pay.total_amount = parking_fee + idle_fee + (res.amount if res.amount > 0 else 0.0)

        if promo_code and isinstance(res.User, Member):
            still_available = any(p.promoCode == promo_code for p in res.User.collected_promotion)
            if not still_available:
                raise HTTPException(status_code=400, detail="Error: Promo code already used or not found")
            for promo in res.User.collected_promotion:
                if promo.validatePromotion(promo_code):
                    pay.use_promotion(promo, pay.total_amount)
                    pay.total_amount = pay.calculateTotal(pay.total_amount)
                    if pay.total_amount < 0:
                        pay.total_amount = 0.0
                    res.User.collected_promotion.remove(promo)
                    break

        success = pay.processPayment(gw)

        if success:
            res.reservation_status = "PAID"
            res.Parking_slot_time.Parking_slot.set_status("AVAILABLE")
            tx = Transaction(res.User, pay)
            res.User.transaction_list.append(tx)
            return f"Payment Success | trans_id={tx.trans_id} | total={pay.total_amount}"

        raise HTTPException(status_code=400, detail="Error: Payment failed (Invalid account/card format)")

    def view_reservation_history(self, uid: str):
        user = self.check_user_id(uid)
        if not user: return "Error: User not found"
        return user.view_reservation_history()

    def view_transaction_history(self, uid: str):
        user = self.check_user_id(uid)
        return user.view_transaction_history() if user else "Error: User not found"



db = Jord_System()
db.User_list.append(User("U01", "Somchai", "081234"))
m01 = Member(User("M01", "Nadech", "089999"))
db.User_list.append(m01)
db.Partner_shop_list.append(Partner_Shop("S01", "Central", "BKK"))

class CarReq(BaseModel): user_id: str; license: str; color: str; brand: str; car_type: str
class RemoveCarReq(BaseModel): user_id: str; license: str
class EditUserReq(BaseModel): user_id: str; name: Optional[str] = None; tele_num: Optional[str] = None
class UpgradeReq(BaseModel):
    user_id: str
    pay_method: str
    acc: Optional[str] = None
    card_no: Optional[str] = None
class RenewReq(BaseModel): member_id: str; pay_method: str; acc: str
class ResReq(BaseModel): user_id: str; license: str; slot_id: str; date: str; time: str
class EVResReq(BaseModel): user_id: str; license: str; slot_id: str; kwh: float; date: str; time: str
class PayReq(BaseModel):
    res_id: str
    method: str
    promo_code: Optional[str] = None
    acc: Optional[str] = None
    card_no: Optional[str] = None
class CancelReq(BaseModel):
    user_id: str
    res_id: str
    pay_method: str
    acc: Optional[str] = None
    card_no: Optional[str] = None
class PointReq(BaseModel): member_id: str; shop_id: str; amount: float
class AddPromoToMemberReq(BaseModel): member_id: str; shop_id: str; promo_code: str
class RedeemReq(BaseModel): member_id: str; points: int
class ClockReq(BaseModel): date: str; time: str
class CheckInReq(BaseModel): user_id: str; res_id: str
class CheckOutReq(BaseModel): user_id: str; res_id: str


# ---- Clock ----
@mcp.tool()
def set_clock(date: str, time: str) -> str:
    """
    ตั้งเวลาของระบบ (Simulated Clock)
    date: รูปแบบ dd-mm-yyyy เช่น 01-01-2025
    time: รูปแบบ hh-mm เช่น 08-30
    """
    return clock.set_time(date, time)

# ---- Slots ----
@mcp.tool()
def check_available_slots() -> List[str]:
    """ดูช่องจอดรถที่ว่างอยู่ทั้งหมดในระบบ"""
    return db.check_available_slots()

# ---- Cars ----
@mcp.tool()
def add_car(user_id: str, license: str, color: str, brand: str, car_type: str) -> str:
    """
    เพิ่มรถให้ผู้ใช้
    car_type: NORMAL | EV | SUPER
    license: ตัวอักษร 2 ตัว + ตัวเลข 4 ตัว เช่น AB1234
    """
    return db.add_car(user_id, license, color, brand, car_type)

@mcp.tool()
def remove_car(user_id: str, license: str) -> str:
    """ลบรถออกจากบัญชีผู้ใช้ (ไม่สามารถลบได้ถ้ามีการจองที่ยังค้างอยู่)"""
    return db.remove_car(user_id, license)

# ---- Users ----
@mcp.tool()
def edit_user_info(user_id: str, name: Optional[str] = None, tele_num: Optional[str] = None) -> str:
    """แก้ไขข้อมูลผู้ใช้ (ชื่อ และ/หรือ เบอร์โทร)"""
    return db.edit_user_info(user_id, name, tele_num)

@mcp.tool()
def upgrade_to_member(user_id: str, pay_method: str, acc: Optional[str] = None, card_no: Optional[str] = None) -> str:
    """
    อัปเกรดผู้ใช้ทั่วไปเป็น Member (ค่าสมัคร 300 บาท)
    pay_method: QR | CREDIT
    acc: เลขบัญชี 8 หลัก (ถ้าใช้ QR)
    card_no: เลขบัตร 6 หลัก (ถ้าใช้ CREDIT)
    """
    return db.upgrade_to_member(user_id, pay_method, acc, card_no)

@mcp.tool()
def renew_membership(member_id: str, pay_method: str, acc: str) -> str:
    """
    ต่ออายุ Membership (ค่าต่ออายุ 500 บาท)
    pay_method: QR | CREDIT
    acc: เลขบัญชี 8 หลัก (QR) หรือ เลขบัตร 6 หลัก (CREDIT)
    """
    return db.renew_membership(member_id, pay_method, acc)

# ---- Reservation ----
@mcp.tool()
def create_reservation(user_id: str, license: str, slot_id: str, date: str, time: str) -> str:
    """
    จองที่จอดรถสำหรับรถปกติ (Normal / Super Car)
    date: dd-mm-yyyy เช่น 01-01-2025
    time: hh-mm เช่น 09-00
    slot_id: เช่น N1, SC2
    """
    try:
        day, month, year = map(int, date.split("-"))
        hour, minute = map(int, time.split("-"))
        target = datetime(year, month, day, hour, minute)
    except Exception:
        return "Error: Invalid date/time format"
    return db.create_reservation(user_id, license, slot_id, target)

@mcp.tool()
def create_ev_reservation(user_id: str, license: str, slot_id: str, kwh: float, date: str, time: str) -> str:
    """
    จองที่จอดรถพร้อมชาร์จไฟสำหรับรถ EV
    slot_id: เช่น EV1
    kwh: จำนวน kWh ที่ต้องการชาร์จ
    date: dd-mm-yyyy
    time: hh-mm
    """
    try:
        day, month, year = map(int, date.split("-"))
        hour, minute = map(int, time.split("-"))
        target = datetime(year, month, day, hour, minute)
    except Exception:
        return "Error: Invalid date/time format"
    return db.create_ev_reservation(user_id, license, slot_id, target, kwh)

@mcp.tool()
def cancel_reservation(user_id: str, res_id: str, pay_method: str, acc: Optional[str] = None, card_no: Optional[str] = None) -> str:
    """
    ยกเลิกการจอง (อาจมีค่าปรับ 100 บาท ถ้ายกเลิกน้อยกว่า 1 ชม. ก่อนเวลาจอง)
    pay_method: QR | CREDIT
    acc: เลขบัญชี 8 หลัก (ถ้าใช้ QR)
    card_no: เลขบัตร 6 หลัก (ถ้าใช้ CREDIT)
    """
    return db.cancel_reservation(user_id, res_id, pay_method, acc, card_no)

@mcp.tool()
def view_reservation_history(user_id: str) -> List[str]:
    """ดูประวัติการจองที่จอดรถของผู้ใช้ (แสดงเวลาเข้า/ออกจริงด้วย)"""
    return db.view_reservation_history(user_id)

# ---- [NEW] Check-in / Check-out ----
@mcp.tool()
def checkin(user_id: str, res_id: str) -> str:
    """
    เช็คอิน: บันทึกเวลาที่รถเข้าจอดจริง
    - Slot status จะเปลี่ยนเป็น OCCUPIED
    - Reservation status จะเปลี่ยนเป็น CheckedIn
    """
    return db.checkin(user_id, res_id)

@mcp.tool()
def checkout(user_id: str, res_id: str) -> str:
    """
    เช็คเอาท์: บันทึกเวลาที่รถออกจริง และแสดงยอดค่าจอดโดยประมาณ
    - Reservation status จะเปลี่ยนเป็น CheckedOut
    - หลังจากนี้ต้องไปชำระเงินด้วย pay
    """
    return db.checkout(user_id, res_id)

# ---- Payment ----
@mcp.tool()
def pay(res_id: str, method: str, acc: Optional[str] = None, card_no: Optional[str] = None, promo_code: Optional[str] = None) -> str:
    """
    ชำระเงินค่าจอดรถ (ต้อง Check-out ก่อน)
    method: QR | CREDIT
    acc: เลขบัญชี 8 หลัก (ถ้าใช้ QR)
    card_no: เลขบัตร 6 หลัก (ถ้าใช้ CREDIT)
    promo_code: โค้ดโปรโมชัน (ถ้ามี เฉพาะ Member)
    """
    req = PayReq(res_id=res_id, method=method, acc=acc, card_no=card_no, promo_code=promo_code)
    try:
        return db.paying(req)
    except HTTPException as e:
        return f"Error: {e.detail}"

@mcp.tool()
def view_transaction_history(user_id: str) -> List[str]:
    """ดูประวัติธุรกรรมการชำระเงินของผู้ใช้"""
    result = db.view_transaction_history(user_id)
    if isinstance(result, str):
        return [result]
    return result

# ---- Points & Promotions ----
@mcp.tool()
def add_point_from_shop(member_id: str, shop_id: str, amount: float) -> str:
    """
    เพิ่ม Point ให้ Member จากการซื้อสินค้าที่ร้านพาร์ทเนอร์
    amount: ยอดซื้อ (ทุก 100 บาท = 1 point)
    """
    return db.add_point_from_shop(member_id, shop_id, amount)

@mcp.tool()
def view_points(member_id: str) -> List[str]:
    """ดู Point คงเหลือและวันหมดอายุของ Member"""
    result = db.view_point_transactions(member_id)
    if isinstance(result, str):
        return [result]
    return result

@mcp.tool()
def redeem_reward(member_id: str, points: int) -> str:
    """
    แลก Point เป็น Promo Code
    points: 100 → REDEEM100 | 200 → REDEEM200
    """
    return db.redeem_reward(member_id, points)

@mcp.tool()
def check_promotions(member_id: str) -> List[str]:
    """ดูโปรโมชันที่ Member มีอยู่ทั้งหมด"""
    result = db.check_promotions(member_id)
    if isinstance(result, str):
        return [result]
    return result

@mcp.tool()
def add_promotion_to_member(member_id: str, shop_id: str, promo_code: str) -> str:
    """
    เพิ่มโปรโมชันให้ Member ผ่านร้านพาร์ทเนอร์
    promo_code: REDEEM100 | REDEEM200
    """
    return db.add_promotion_to_member(member_id, shop_id, promo_code)

@mcp.tool()
def get_reward_catalog() -> List[str]:
    """ดูรายการรางวัลที่แลก Point ได้ทั้งหมด"""
    catalog = Promotion("", 0).get_reward_catalog()
    return [f"points_required={r.points_required} | promo_code={r.promo_code}" for r in catalog]

#---- Shops ----
@mcp.tool()
def view_shop_validation_history(shop_id: str) -> List[str]:
    """ดูประวัติการให้ Point แก่ Member ของร้านพาร์ทเนอร์"""
    return db.view_shop_validation_history(shop_id)

@app.post("/cars/add", tags=["Cars"])
def add_car_api(req: CarReq):
    return {"message": db.add_car(req.user_id, req.license, req.color, req.brand, req.car_type)}

@app.delete("/cars/remove", tags=["Cars"])
def remove_car_api(req: RemoveCarReq):
    res = db.remove_car(req.user_id, req.license)
    if "Error" in res: raise HTTPException(status_code=400, detail=res)
    return {"message": res}

@app.patch("/users/edit", tags=["Users"])
def edit_user_api(req: EditUserReq):
    res = db.edit_user_info(req.user_id, req.name, req.tele_num)
    if "Error" in res: raise HTTPException(status_code=400, detail=res)
    return {"message": res}

@app.post("/upgrade", tags=["Users"])
def upgrade_api(req: UpgradeReq):
    res = db.upgrade_to_member(req.user_id, req.pay_method, req.acc, req.card_no)
    if "Error" in res: raise HTTPException(status_code=400, detail=res)
    return {"message": res}

@app.post("/renew", tags=["Users"])
def renew_api(req: RenewReq):
    return {"message": db.renew_membership(req.member_id, req.pay_method, req.acc)}

@app.post("/reserve", tags=["Reservation"])
def reserve_api(req: ResReq):
    try:
        day, month, year = map(int, req.date.split("-"))
        hour, minute = map(int, req.time.split("-"))
        target = datetime(year, month, day, hour, minute)
    except Exception:
        raise HTTPException(status_code=400, detail="Error: Invalid date/time format")
    return db.create_reservation(req.user_id, req.license, req.slot_id, target)

@app.post("/reserve/ev", tags=["Reservation"])
def ev_reserve_api(req: EVResReq):
    try:
        day, month, year = map(int, req.date.split("-"))
        hour, minute = map(int, req.time.split("-"))
        target = datetime(year, month, day, hour, minute)
    except Exception:
        raise HTTPException(status_code=400, detail="Error: Invalid date/time format")
    res = db.create_ev_reservation(req.user_id, req.license, req.slot_id, target, req.kwh)
    if isinstance(res, str) and "Error" in res:
        raise HTTPException(status_code=400, detail=res)
    return res

@app.post("/checkin", tags=["Reservation"])
def checkin_api(req: CheckInReq):
    res = db.checkin(req.user_id, req.res_id)
    if "Error" in res: raise HTTPException(status_code=400, detail=res)
    return {"message": res}

@app.post("/checkout", tags=["Reservation"])
def checkout_api(req: CheckOutReq):
    res = db.checkout(req.user_id, req.res_id)
    if "Error" in res: raise HTTPException(status_code=400, detail=res)
    return {"message": res}

@app.post("/pay", tags=["Payment"])
def pay_api(req: PayReq):
    return db.paying(req)

@app.post("/cancel", tags=["Reservation"])
def api_cancel(req: CancelReq):
    res = db.cancel_reservation(req.user_id, req.res_id, req.pay_method, req.acc, req.card_no)
    if "Error" in res: raise HTTPException(status_code=400, detail=res)
    return {"message": res}

@app.get("/reservations/{user_id}", tags=["Reservation"])
def reservation_history_api(user_id: str):
    res = db.view_reservation_history(user_id)
    if isinstance(res, str) and "Error" in res:
        raise HTTPException(status_code=400, detail=res)
    return {"reservations": res}

@app.get("/history/{user_id}", tags=["History"])
def history_api(user_id: str):
    return {"history": db.view_transaction_history(user_id)}

@app.get("/points/{user_id}", tags=["Points"])
def view_points_api(user_id: str):
    res = db.view_point_transactions(user_id)
    if isinstance(res, str) and "Error" in res:
        raise HTTPException(status_code=400, detail=res)
    return {"points": res}

@app.post("/point/add", tags=["Points"])
def api_point(req: PointReq):
    res = db.add_point_from_shop(req.member_id, req.shop_id, req.amount)
    if "Error" in res: raise HTTPException(status_code=400, detail=res)
    return {"message": res}

@app.post("/points/redeem", tags=["Points"])
def redeem_api(req: RedeemReq):
    res = db.redeem_reward(req.member_id, req.points)
    if isinstance(res, str) and "Error" in res:
        raise HTTPException(status_code=400, detail=res)
    return {"message": res}

@app.get("/rewards/catalog", tags=["Points"])
def get_reward_catalog():
    catalog = Promotion("", 0).get_reward_catalog()
    return {"rewards": [
        f"points_required={r.points_required} | promo_code={r.promo_code}"
        for r in catalog
    ]}

@app.post("/promotions/add-to-member", tags=["Shops"])
def add_promo_to_member_api(req: AddPromoToMemberReq):
    res = db.add_promotion_to_member(req.member_id, req.shop_id, req.promo_code)
    if "Error" in res: raise HTTPException(status_code=400, detail=res)
    return {"message": res}

@app.get("/promotions/{member_id}", tags=["Promotions"])
def check_promotions_api(member_id: str):
    res = db.check_promotions(member_id)
    if isinstance(res, str) and "Error" in res:
        raise HTTPException(status_code=400, detail=res)
    return {"promotions": res}

@app.post("/clock/set", tags=["Clock"])
def set_clock(req: ClockReq):
    result = clock.set_time(req.date, req.time)
    if "Error" in result:
        raise HTTPException(status_code=400, detail=result)
    return {"message": result}

@app.get("/clock/get", tags=["Clock"])
def get_clock():
    return {"current_time": clock.get_time()}

@app.get("/slots/available", tags=["Slots"])
def available_slots_api():
    return {"available_slots": db.check_available_slots()}

@app.get("/shops/{shop_id}/history", tags=["Shops"])
def shop_history_api(shop_id: str):
    res = db.view_shop_validation_history(shop_id)
    if res and "Error" in res[0]:
        raise HTTPException(status_code=400, detail=res[0])
    return {"validation_history": res}

if __name__ == "__main__":
    import sys
    import threading
    import uvicorn

    if len(sys.argv) > 1 and sys.argv[1] == "api":
        uvicorn.run(app, host="0.0.0.0", port=8000)
    elif len(sys.argv) > 1 and sys.argv[1] == "both":
        t = threading.Thread(
            target=uvicorn.run,
            args=(app,),
            kwargs={"host": "0.0.0.0", "port": 8000},
            daemon=True
        )
        t.start()
        mcp.run()
    else:
        mcp.run()