"""
generators.py - Iterator and Generator Exercises

Tasks:
1. Generator for squares up to N
2. Generator for even numbers 0 to n
3. Generator for numbers divisible by 3 and 4
4. Generator for squares from a to b
5. Generator for countdown from n to 0
"""


# ============================================================================
# TASK 1: Generator for squares up to N
# ============================================================================

def squares_up_to_n(n):
    """
    Generator that yields squares of numbers from 1 to n
    
    Parameters:
    n (int): Upper limit (inclusive)
    
    Yields:
    int: Square of each number
    """
    for i in range(1, n + 1):
        yield i ** 2  # yield pauses function and returns value


def task1_squares(n=10):
    """Test squares generator"""
    print(f"\n=== Task 1: Squares up to {n} ===")
    
    # Use generator in for loop
    for square in squares_up_to_n(n):
        print(f"  {square}", end=" ")
    print()
    
    # Or convert to list
    squares_list = list(squares_up_to_n(n))
    print(f"  As list: {squares_list}")


# ============================================================================
# TASK 2: Generator for even numbers
# ============================================================================

def even_numbers(n):
    """
    Generator that yields even numbers from 0 to n
    
    Parameters:
    n (int): Upper limit (inclusive)
    
    Yields:
    int: Even numbers
    """
    for i in range(0, n + 1, 2):  # step=2 gives only even numbers
        yield i


def task2_evens(n=20):
    """Test even numbers generator"""
    print(f"\n=== Task 2: Even numbers 0 to {n} ===")
    
    # Get generator
    evens = even_numbers(n)
    
    # Print comma-separated
    result = ", ".join(str(num) for num in evens)
    print(f"  {result}")


# ============================================================================
# TASK 3: Generator for numbers divisible by 3 AND 4
# ============================================================================

def divisible_by_3_and_4(n):
    """
    Generator for numbers divisible by both 3 and 4 (i.e., by 12)
    
    Parameters:
    n (int): Upper limit (inclusive)
    
    Yields:
    int: Numbers divisible by 12
    """
    # A number divisible by both 3 and 4 is divisible by LCM(3,4) = 12
    for i in range(0, n + 1, 12):  # Step by 12 for efficiency
        yield i
    
    # Alternative (less efficient but more explicit):
    # for i in range(n + 1):
    #     if i % 3 == 0 and i % 4 == 0:
    #         yield i


def task3_divisible(n=100):
    """Test divisible by 3 and 4 generator"""
    print(f"\n=== Task 3: Divisible by 3 and 4 (0 to {n}) ===")
    
    result = list(divisible_by_3_and_4(n))
    print(f"  {result}")
    print(f"  Count: {len(result)} numbers")


# ============================================================================
# TASK 4: Generator for squares from a to b
# ============================================================================

def squares_range(a, b):
    """
    Generator that yields squares of numbers from a to b (inclusive)
    
    Parameters:
    a (int): Start value
    b (int): End value
    
    Yields:
    int: Square of each number in range
    """
    for i in range(a, b + 1):
        yield i ** 2


def task4_squares_range(a=3, b=7):
    """Test squares range generator"""
    print(f"\n=== Task 4: Squares from {a} to {b} ===")
    
    print("  Using for loop:")
    for value in squares_range(a, b):
        print(f"    {value}")
    
    # Also demonstrate manual iteration with next()
    print("  Using next():")
    gen = squares_range(a, b)
    try:
        while True:
            print(f"    {next(gen)}", end=" ")
    except StopIteration:
        print("\n    [Generator exhausted]")


# ============================================================================
# TASK 5: Generator for countdown from n to 0
# ============================================================================

def countdown(n):
    """
    Generator that counts down from n to 0
    
    Parameters:
    n (int): Starting value
    
    Yields:
    int: Numbers from n down to 0
    """
    while n >= 0:
        yield n
        n -= 1


def task5_countdown(n=10):
    """Test countdown generator"""
    print(f"\n=== Task 5: Countdown from {n} ===")
    
    result = list(countdown(n))
    print(f"  {result}")
    
    # Show it works in for loop
    print("  Countdown: ", end="")
    for num in countdown(5):
        print(f"{num} ", end="")
    print("🚀")


def main():
    """Run all generator exercises"""
    print("\n" + "="*60)
    print("GENERATORS EXERCISES")
    print("="*60)
    
    task1_squares(10)
    task2_evens(20)
    task3_divisible(100)
    task4_squares_range(3, 7)
    task5_countdown(10)
    
    print("\n✓ All generator exercises complete\n")


if __name__ == "__main__":
    main()