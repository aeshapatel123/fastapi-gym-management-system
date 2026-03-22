# Gym Management System - FastAPI Project

## Project Overview
This project is a backend system built using FastAPI to manage gym memberships, plans, and class bookings.

## Features
- REST APIs using FastAPI
- Pydantic validation
- CRUD operations
- Membership management
- Class booking system
- Search, filtering, sorting
- Pagination and combined browsing

## Endpoints Covered
- GET, POST, PUT, DELETE
- Multi-step workflows (Membership → Booking → Freeze/Reactivate)
- Advanced APIs (Search, Sort, Pagination, Browse)

## Tech Stack
- Python
- FastAPI
- Uvicorn

## Run Project
```bash
uvicorn main:app --reload