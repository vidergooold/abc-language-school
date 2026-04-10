from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional
from datetime import datetime, date, timedelta
from pydantic import BaseModel
import sys
sys.path.append('..')

from database import get_db
from models import (
    Payment, Expense, RevenueAnalytics, Enrollment, Course,
    User, PaymentStatus, UserRole
)

router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["analytics"]
)

# Pydantic schemas
class RevenueReport(BaseModel):
    period_start: date
    period_end: date
    total_revenue: float
    total_expenses: float
    net_profit: float
    profit_margin: float
    active_students: int
    new_students: int
    revenue_per_student: float

class MonthlyBreakdown(BaseModel):
    month: str
    revenue: float
    expenses: float
    profit: float

class CourseRevenue(BaseModel):
    course_id: int
    course_name: str
    total_revenue: float
    enrollment_count: int
    average_price: float

@router.get("/revenue-report", response_model=RevenueReport)
def get_revenue_report(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive revenue report for a given period.
    Includes revenue, expenses, profit, and student metrics.
    """
    # Calculate total revenue from completed payments
    total_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.status == PaymentStatus.completed,
        Payment.created_at >= start_date,
        Payment.created_at <= end_date
    ).scalar() or 0.0
    
    # Calculate total expenses
    total_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.date >= start_date,
        Expense.date <= end_date
    ).scalar() or 0.0
    
    # Calculate net profit
    net_profit = total_revenue - total_expenses
    
    # Calculate profit margin
    profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Count active students
    active_students = db.query(func.count(User.id)).filter(
        User.role == UserRole.student,
        User.is_active == True
    ).scalar() or 0
    
    # Count new students in period
    new_students = db.query(func.count(User.id)).filter(
        User.role == UserRole.student,
        User.created_at >= start_date,
        User.created_at <= end_date
    ).scalar() or 0
    
    # Calculate revenue per student
    revenue_per_student = total_revenue / active_students if active_students > 0 else 0
    
    return RevenueReport(
        period_start=start_date,
        period_end=end_date,
        total_revenue=round(total_revenue, 2),
        total_expenses=round(total_expenses, 2),
        net_profit=round(net_profit, 2),
        profit_margin=round(profit_margin, 2),
        active_students=active_students,
        new_students=new_students,
        revenue_per_student=round(revenue_per_student, 2)
    )

@router.get("/monthly-breakdown", response_model=List[MonthlyBreakdown])
def get_monthly_breakdown(
    year: int,
    db: Session = Depends(get_db)
):
    """
    Get monthly revenue/expense breakdown for a year.
    """
    monthly_data = []
    
    for month in range(1, 13):
        # Calculate revenue for the month
        month_revenue = db.query(func.sum(Payment.amount)).filter(
            Payment.status == PaymentStatus.completed,
            extract('year', Payment.created_at) == year,
            extract('month', Payment.created_at) == month
        ).scalar() or 0.0
        
        # Calculate expenses for the month
        month_expenses = db.query(func.sum(Expense.amount)).filter(
            extract('year', Expense.date) == year,
            extract('month', Expense.date) == month
        ).scalar() or 0.0
        
        month_profit = month_revenue - month_expenses
        
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        
        monthly_data.append(MonthlyBreakdown(
            month=month_names[month - 1],
            revenue=round(month_revenue, 2),
            expenses=round(month_expenses, 2),
            profit=round(month_profit, 2)
        ))
    
    return monthly_data

@router.get("/course-revenue", response_model=List[CourseRevenue])
def get_course_revenue(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Analyze revenue by course.
    Shows which courses are most profitable.
    """
    # Query to get revenue per course
    query = db.query(
        Course.id,
        Course.name,
        func.sum(Payment.amount).label('total_revenue'),
        func.count(Enrollment.id).label('enrollment_count'),
        func.avg(Payment.amount).label('average_price')
    ).join(
        Enrollment, Course.id == Enrollment.course_id
    ).join(
        Payment, Enrollment.payment_id == Payment.id
    ).filter(
        Payment.status == PaymentStatus.completed
    )
    
    if start_date:
        query = query.filter(Payment.created_at >= start_date)
    if end_date:
        query = query.filter(Payment.created_at <= end_date)
    
    results = query.group_by(Course.id, Course.name).all()
    
    course_revenues = [
        CourseRevenue(
            course_id=row[0],
            course_name=row[1],
            total_revenue=round(float(row[2] or 0), 2),
            enrollment_count=row[3] or 0,
            average_price=round(float(row[4] or 0), 2)
        )
        for row in results
    ]
    
    # Sort by total revenue descending
    course_revenues.sort(key=lambda x: x.total_revenue, reverse=True)
    
    return course_revenues

@router.get("/expense-breakdown")
def get_expense_breakdown(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """
    Break down expenses by category.
    """
    expenses = db.query(
        Expense.category,
        func.sum(Expense.amount).label('total_amount'),
        func.count(Expense.id).label('count')
    ).filter(
        Expense.date >= start_date,
        Expense.date <= end_date
    ).group_by(Expense.category).all()
    
    total_expenses = sum(exp[1] for exp in expenses)
    
    breakdown = [
        {
            "category": exp[0],
            "total_amount": round(float(exp[1]), 2),
            "count": exp[2],
            "percentage": round(float(exp[1]) / total_expenses * 100, 2) if total_expenses > 0 else 0
        }
        for exp in expenses
    ]
    
    return {
        "total_expenses": round(total_expenses, 2),
        "breakdown": breakdown
    }

@router.get("/payment-stats")
def get_payment_stats(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Get payment statistics: success rate, average amount, etc.
    """
    query = db.query(Payment)
    
    if start_date:
        query = query.filter(Payment.created_at >= start_date)
    if end_date:
        query = query.filter(Payment.created_at <= end_date)
    
    total_payments = query.count()
    completed_payments = query.filter(Payment.status == PaymentStatus.completed).count()
    failed_payments = query.filter(Payment.status == PaymentStatus.failed).count()
    pending_payments = query.filter(Payment.status == PaymentStatus.pending).count()
    
    total_amount = db.query(func.sum(Payment.amount)).filter(
        Payment.status == PaymentStatus.completed
    )
    if start_date:
        total_amount = total_amount.filter(Payment.created_at >= start_date)
    if end_date:
        total_amount = total_amount.filter(Payment.created_at <= end_date)
    
    total_amount = total_amount.scalar() or 0.0
    
    avg_payment = total_amount / completed_payments if completed_payments > 0 else 0
    
    return {
        "total_payments": total_payments,
        "completed": completed_payments,
        "failed": failed_payments,
        "pending": pending_payments,
        "success_rate": round(completed_payments / total_payments * 100, 2) if total_payments > 0 else 0,
        "total_amount": round(total_amount, 2),
        "average_payment": round(avg_payment, 2)
    }

@router.get("/student-lifetime-value")
def get_student_lifetime_value(db: Session = Depends(get_db)):
    """
    Calculate average lifetime value of students.
    """
    # Get all students with their total payments
    student_values = db.query(
        User.id,
        User.full_name,
        func.sum(Payment.amount).label('total_paid'),
        func.count(Payment.id).label('payment_count')
    ).join(
        Payment, User.id == Payment.user_id
    ).filter(
        User.role == UserRole.student,
        Payment.status == PaymentStatus.completed
    ).group_by(User.id, User.full_name).all()
    
    if not student_values:
        return {
            "average_lifetime_value": 0,
            "total_students_analyzed": 0,
            "highest_value": 0,
            "lowest_value": 0
        }
    
    values = [float(sv[2]) for sv in student_values]
    
    return {
        "average_lifetime_value": round(sum(values) / len(values), 2),
        "total_students_analyzed": len(student_values),
        "highest_value": round(max(values), 2),
        "lowest_value": round(min(values), 2),
        "median_value": round(sorted(values)[len(values) // 2], 2)
    }

@router.post("/generate-period-report", status_code=status.HTTP_201_CREATED)
def generate_period_report(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """
    Generate and save a revenue analytics report for a period.
    """
    # Get revenue report data
    report = get_revenue_report(start_date, end_date, db)
    
    # Count courses
    course_count = db.query(func.count(Course.id)).filter(
        Course.is_active == True
    ).scalar() or 0
    
    # Create analytics record
    analytics = RevenueAnalytics(
        period_start=start_date,
        period_end=end_date,
        total_revenue=report.total_revenue,
        total_expenses=report.total_expenses,
        net_profit=report.net_profit,
        student_count=report.active_students,
        course_count=course_count,
        average_revenue_per_student=report.revenue_per_student
    )
    
    db.add(analytics)
    db.commit()
    db.refresh(analytics)
    
    return {
        "message": "Revenue analytics report generated successfully",
        "report_id": analytics.id,
        "summary": report
    }
