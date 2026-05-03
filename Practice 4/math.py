"""
math.py - Math Module Exercises

Tasks:
1. Convert degree to radian
2. Calculate area of trapezoid
3. Calculate area of regular polygon
4. Calculate area of parallelogram
"""

import math


# ============================================================================
# TASK 1: Convert degree to radian
# ============================================================================

def degree_to_radian(degree):
    """
    Convert angle from degrees to radians
    
    Formula: radians = degrees × (π / 180)
    
    Parameters:
    degree (float): Angle in degrees
    
    Returns:
    float: Angle in radians
    """
    # Method 1: Using math.radians() (built-in, recommended)
    return math.radians(degree)
    
    # Method 2: Manual calculation
    # return degree * (math.pi / 180)


def task1_degree_to_radian():
    """Test degree to radian conversion"""
    print("\n=== Task 1: Degree to Radian ===")
    
    degree = 15
    radian = degree_to_radian(degree)
    
    print(f"Input degree: {degree}")
    print(f"Output radian: {radian:.6f}")
    
    # Verify: 15° = π/12 ≈ 0.261799
    expected = math.pi / 12
    print(f"Expected (π/12): {expected:.6f}")


# ============================================================================
# TASK 2: Area of trapezoid
# ============================================================================

def trapezoid_area(height, base1, base2):
    """
    Calculate area of a trapezoid
    
    Formula: Area = (base1 + base2) / 2 × height
    
    Parameters:
    height (float): Height of trapezoid
    base1 (float): Length of first base
    base2 (float): Length of second base
    
    Returns:
    float: Area of trapezoid
    """
    return ((base1 + base2) / 2) * height


def task2_trapezoid():
    """Test trapezoid area calculation"""
    print("\n=== Task 2: Area of Trapezoid ===")
    
    height = 5
    base1 = 5
    base2 = 6
    
    area = trapezoid_area(height, base1, base2)
    
    print(f"Height: {height}")
    print(f"Base 1: {base1}")
    print(f"Base 2: {base2}")
    print(f"Expected Output: {area}")


# ============================================================================
# TASK 3: Area of regular polygon
# ============================================================================

def regular_polygon_area(sides, side_length):
    """
    Calculate area of a regular polygon
    
    Formula: Area = (n × s²) / (4 × tan(π/n))
    where n = number of sides, s = side length
    
    Parameters:
    sides (int): Number of sides (must be >= 3)
    side_length (float): Length of each side
    
    Returns:
    float: Area of polygon
    """
    if sides < 3:
        raise ValueError("Polygon must have at least 3 sides")
    
    # Calculate using the formula
    # math.tan() expects radians, math.pi is π
    area = (sides * side_length ** 2) / (4 * math.tan(math.pi / sides))
    
    return area


def task3_polygon():
    """Test regular polygon area calculation"""
    print("\n=== Task 3: Area of Regular Polygon ===")
    
    sides = 4      # Square
    side_length = 25
    
    area = regular_polygon_area(sides, side_length)
    
    print(f"Input number of sides: {sides}")
    print(f"Input the length of a side: {side_length}")
    print(f"The area of the polygon is: {area}")
    
    # Verify: Square with side 25 should have area 25² = 625
    if sides == 4:
        expected = side_length ** 2
        print(f"Verification (square): {side_length}² = {expected}")


# ============================================================================
# TASK 4: Area of parallelogram
# ============================================================================

def parallelogram_area(base, height):
    """
    Calculate area of a parallelogram
    
    Formula: Area = base × height
    
    Parameters:
    base (float): Length of base
    height (float): Height perpendicular to base
    
    Returns:
    float: Area of parallelogram
    """
    return base * height


def task4_parallelogram():
    """Test parallelogram area calculation"""
    print("\n=== Task 4: Area of Parallelogram ===")
    
    base = 5
    height = 6
    
    area = parallelogram_area(base, height)
    
    print(f"Length of base: {base}")
    print(f"Height of parallelogram: {height}")
    print(f"Expected Output: {area}")


# ============================================================================
# BONUS: Additional math exercises
# ============================================================================

def bonus_math_functions():
    """Demonstrate additional math module functions"""
    print("\n=== Bonus: Math Module Functions ===")
    
    # Built-in functions
    print(f"min(3, 7, 1, 9) = {min(3, 7, 1, 9)}")
    print(f"max(3, 7, 1, 9) = {max(3, 7, 1, 9)}")
    print(f"abs(-15) = {abs(-15)}")
    print(f"round(3.14159, 2) = {round(3.14159, 2)}")
    print(f"pow(2, 8) = {pow(2, 8)}")
    
    # math module functions
    print(f"\nmath.sqrt(144) = {math.sqrt(144)}")
    print(f"math.ceil(4.2) = {math.ceil(4.2)}")
    print(f"math.floor(4.8) = {math.floor(4.8)}")
    print(f"math.sin(math.pi/2) = {math.sin(math.pi/2)}")
    print(f"math.cos(0) = {math.cos(0)}")
    print(f"math.pi = {math.pi}")
    print(f"math.e = {math.e}")
    
    # random module (if needed)
    import random
    print(f"\nrandom.random() = {random.random():.4f}")
    print(f"random.randint(1, 10) = {random.randint(1, 10)}")
    print(f"random.choice(['A', 'B', 'C']) = {random.choice(['A', 'B', 'C'])}")
    
    items = [1, 2, 3, 4, 5]
    random.shuffle(items)
    print(f"random.shuffle([1,2,3,4,5]) = {items}")


def main():
    """Run all math exercises"""
    print("\n" + "="*60)
    print("MATH EXERCISES")
    print("="*60)
    
    task1_degree_to_radian()
    task2_trapezoid()
    task3_polygon()
    task4_parallelogram()
    bonus_math_functions()
    
    print("\n✓ All math exercises complete\n")


if __name__ == "__main__":
    main()