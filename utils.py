def print_dashes(func):
    def wrapper(*args, **kwargs):
        print("\n" + "=" * 50)
        result = func(*args, **kwargs)
        
        print("=" * 50 + "\n")  # Bottom dash
        return result
    
    return wrapper