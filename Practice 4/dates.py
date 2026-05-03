"""
dates.py - Date and Time Exercises

Tasks:
1. Subtract five days from current date
2. Print yesterday, today, tomorrow
3. Drop microseconds from datetime
4. Calculate two date difference in seconds
"""

from datetime import datetime, timedelta


def task1_subtract_days(days=5):
    """
    Subtract specified days from current date
    
    Parameters:
    days (int): Number of days to subtract (default: 5)
    
    Returns:
    datetime: Date after subtraction
    """
    print(f"\n=== Task 1: Subtract {days} days ===")
    
    # Get current date and time
    today = datetime.now()
    print(f"Today: {today}")
    
    # Subtract days using timedelta
    result = today - timedelta(days=days)
    print(f"{days} days ago: {result}")
    
    return result


def task2_yesterday_today_tomorrow():
    """
    Print yesterday, today, and tomorrow
    
    Returns:
    tuple: (yesterday, today, tomorrow) as datetime objects
    """
    print("\n=== Task 2: Yesterday, Today, Tomorrow ===")
    
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    
    print(f"Yesterday: {yesterday.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Today:     {today.strftime('%Y-%m-%m-%d %H:%M:%S')}")
    print(f"Tomorrow:  {tomorrow.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return yesterday, today, tomorrow


def task3_drop_microseconds():
    """
    Drop microseconds from current datetime
    
    Returns:
    datetime: Datetime with microseconds set to 0
    """
    print("\n=== Task 3: Drop Microseconds ===")
    
    # Get current time with microseconds
    now_with_micro = datetime.now()
    print(f"With microseconds: {now_with_micro}")
    
    # Method 1: Replace microseconds with 0
    now_no_micro = now_with_micro.replace(microsecond=0)
    print(f"Without microseconds: {now_no_micro}")
    
    # Method 2: Using replace() is cleaner than string manipulation
    return now_no_micro


def task4_date_difference_seconds():
    """
    Calculate difference between two dates in seconds
    
    Returns:
    float: Difference in seconds
    """
    print("\n=== Task 4: Date Difference in Seconds ===")
    
    # Create two example dates
    date1 = datetime(2024, 1, 1, 12, 0, 0)
    date2 = datetime(2024, 1, 15, 18, 30, 45)
    
    print(f"Date 1: {date1}")
    print(f"Date 2: {date2}")
    
    # Calculate difference (returns timedelta object)
    difference = date2 - date1
    
    # Convert to total seconds
    seconds = difference.total_seconds()
    
    print(f"Difference: {difference}")
    print(f"In seconds: {seconds:,}")
    
    # Also show breakdown
    days = difference.days
    hours = difference.seconds // 3600
    minutes = (difference.seconds % 3600) // 60
    secs = difference.seconds % 60
    
    print(f"Breakdown: {days} days, {hours} hours, {minutes} minutes, {secs} seconds")
    
    return seconds


def main():
    """Run all date exercises"""
    print("\n" + "="*60)
    print("DATES EXERCISES")
    print("="*60)
    
    task1_subtract_days()
    task2_yesterday_today_tomorrow()
    task3_drop_microseconds()
    task4_date_difference_seconds()
    
    print("\n✓ All date exercises complete\n")


if __name__ == "__main__":
    main()