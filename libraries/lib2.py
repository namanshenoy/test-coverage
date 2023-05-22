# Fizz Buzz takes in a number and returns the fizzbuzz representation of it.
def fizzbuzz(num: int) -> str:
    if num == 0:
        return "0"
    elif num % 15 == 0:
        return "fizzbuzz"
    elif num % 5 == 0:
        return "buzz"
    elif num % 3 == 0:
        return "fizz"
    else:
        return str(num)


def get_fizz_buzz(max_num: int) -> str:
    values = [fizzbuzz(n) for n in range(max_num)]
    return ",".join(values)
