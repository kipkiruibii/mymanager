import time
import random
import string

def generate_transaction_id():
    # Get current timestamp
    timestamp = int(time.time())

    # Generate random characters
    random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=5))

    # Combine timestamp and random characters
    transaction_id = f'{timestamp}{random_chars}'

    return transaction_id

# Example usage
print(generate_transaction_id())
