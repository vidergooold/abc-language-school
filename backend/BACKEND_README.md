# ABC Language School - Advanced Backend System

## Overview
Comprehensive backend system for managing a language school with 15+ database tables, advanced scheduling logic, automated notifications, and detailed economic analytics.

## Database Architecture

### 15 Comprehensive Tables:

1. **Users** - Student, teacher, admin, and manager accounts
2. **Courses** - Language courses with levels (beginner to advanced)
3. **Groups** - Course groups with enrollment tracking
4. **Lessons** - Individual lessons with schedule management
5. **Rooms** - Classroom management and availability
6. **Enrollments** - Student course enrollments
7. **Payments** - Payment processing and tracking
8. **Attendance** - Student attendance records
9. **News** - Article publishing system with draft/published states
10. **Notifications** - Automated notification scheduling
11. **Waitlist** - Course waitlist management
12. **Reviews** - Course reviews and ratings
13. **Materials** - Course materials and resources
14. **Expenses** - Business expense tracking
15. **Revenue Analytics** - Automated financial reports

## Key Features

### 1. Advanced Schedule Management (routers/scheduler.py)
- **Conflict Prevention**: Automatic detection of scheduling conflicts
  - Teacher cannot have overlapping lessons
  - Rooms cannot be double-booked
  - Groups cannot have conflicting schedules
- **Time Overlap Validation**: Smart time range conflict detection
- **Available Room Finder**: Real-time room availability checking
- **Teacher Schedule View**: Complete teacher schedule management

### 2. Automated Notification System (routers/notifications.py)
- **Scheduled Notifications**: Background task processing
- **Bulk Notifications**: Mass notifications for announcements
- **Role-Based Targeting**: Send to specific user roles
- **Multiple Channels**: Email, SMS, push notification support
- **Statistics & Monitoring**: Track sent/pending/failed notifications
- **Cron-Compatible**: Endpoint for scheduled notification sending

### 3. Economic Analytics (routers/analytics.py)
- **Revenue Reports**: Comprehensive financial analysis
  - Total revenue, expenses, net profit
  - Profit margins
  - Revenue per student
- **Monthly Breakdowns**: Year-over-year analysis
- **Course Profitability**: Revenue analysis by course
- **Expense Categorization**: Detailed expense breakdowns
- **Payment Statistics**: Success rates and average amounts
- **Student Lifetime Value**: Customer value calculations
- **Automated Report Generation**: Saved analytics reports

## Installation

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Database
```bash
# Initialize database (creates all 15 tables)
python init_db.py

# Populate with sample data
python seeds/seed_all.py
```

### 3. Run the Server
```bash
cd app
uvicorn main:app --reload
```

## API Endpoints

### Scheduler
- `POST /api/v1/scheduler/lessons` - Create lesson with conflict check
- `POST /api/v1/scheduler/check-conflicts` - Check for conflicts
- `GET /api/v1/scheduler/lessons` - Get lessons with filters
- `GET /api/v1/scheduler/available-rooms` - Find available rooms
- `GET /api/v1/scheduler/teacher-schedule/{id}` - Teacher schedule

### Notifications
- `POST /api/v1/notifications/` - Schedule single notification
- `POST /api/v1/notifications/bulk` - Bulk notifications
- `GET /api/v1/notifications/` - Get notifications
- `GET /api/v1/notifications/pending` - Get pending notifications
- `POST /api/v1/notifications/send-pending` - Trigger sending
- `GET /api/v1/notifications/stats` - Notification statistics

### Analytics
- `GET /api/v1/analytics/revenue-report` - Comprehensive revenue report
- `GET /api/v1/analytics/monthly-breakdown` - Monthly data
- `GET /api/v1/analytics/course-revenue` - Revenue by course
- `GET /api/v1/analytics/expense-breakdown` - Expense categories
- `GET /api/v1/analytics/payment-stats` - Payment statistics
- `GET /api/v1/analytics/student-lifetime-value` - LTV analysis
- `POST /api/v1/analytics/generate-period-report` - Save report

## Business Logic Examples

### Example 1: Create Lesson with Conflict Prevention
```python
# Automatically checks for:
# - Teacher availability
# - Room availability  
# - Group schedule conflicts
POST /api/v1/scheduler/lessons
{
    "group_id": 1,
    "teacher_id": 5,
    "room_id": 3,
    "date": "2025-02-15",
    "start_time": "14:00",
    "end_time": "15:30",
    "topic": "Business English"
}
```

### Example 2: Send Bulk Notification
```python
# Send to all students
POST /api/v1/notifications/bulk
{
    "title": "School Holiday Announcement",
    "message": "School will be closed next Monday",
    "notification_type": "email",
    "scheduled_at": "2025-02-10T09:00:00",
    "role_filter": "student"
}
```

### Example 3: Generate Revenue Report
```python
# Get detailed financial analysis
GET /api/v1/analytics/revenue-report?start_date=2025-01-01&end_date=2025-01-31

Response:
{
    "total_revenue": 450000.00,
    "total_expenses": 280000.00,
    "net_profit": 170000.00,
    "profit_margin": 37.78,
    "active_students": 150,
    "new_students": 25,
    "revenue_per_student": 3000.00
}
```

## Technologies

- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM and database management
- **PostgreSQL** - Primary database
- **Pydantic** - Data validation
- **Python 3.9+** - Programming language

## Key Improvements Over Previous Version

1. **More Tables**: Increased from basic setup to 15 comprehensive tables
2. **Advanced Logic**: Conflict prevention, automated notifications, analytics
3. **Business Features**: 
   - Article publishing with draft/published workflow
   - Automated notification scheduling
   - Economic analysis and reporting
4. **Real Data**: Integration with Excel data from actual school operations
5. **Production-Ready**: Proper error handling, validation, and documentation

## Development

### Project Structure
```
backend/
├── app/
│   ├── main.py              # Main application
│   ├── database.py          # Database configuration  
│   ├── models.py            # 15 SQLAlchemy models
│   └── routers/
│       ├── scheduler.py     # Schedule management
│       ├── notifications.py # Notification system
│       └── analytics.py     # Financial analytics
├── init_db.py              # Database initialization
├── seeds/
│   └── seed_all.py         # Unified seed script
└── requirements.txt        # Python dependencies
```

## Future Enhancements

- Real-time notification delivery (WebSockets)
- Advanced reporting dashboards
- Machine learning for student success prediction
- Integration with payment gateways
- Mobile app API endpoints
- Multi-language support

## License

This project is part of the ABC Language School graduation project.
