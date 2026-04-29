import sys
import traceback
from app import predict_logic

try:
    print("Testing prediction logic for 강남구...")
    result = predict_logic("강남구", 10000)
    print("Result:", result)
except Exception as e:
    print("Caught Exception:")
    traceback.print_exc()
