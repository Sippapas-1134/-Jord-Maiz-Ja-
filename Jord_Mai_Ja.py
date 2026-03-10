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