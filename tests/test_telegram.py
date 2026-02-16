"""
텔레그램 메시지 전송 테스트

이 파일은 텔레그램 메시지 전송 기능이 
정상적으로 작동하는지 확인합니다.
"""

import sys
import os
from datetime import datetime

# src 폴더를 import 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.telegram import send_telegram


def main():
    """텔레그램 메시지 전송 테스트를 실행합니다."""
    
    print("=" * 50)
    print("📱 텔레그램 메시지 전송 테스트 시작")
    print("=" * 50)
    print()
    
    # 현재 시간을 포함한 테스트 메시지
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    test_message = f"""
🤖 자동매매 봇 테스트 메시지

현재 시간: {current_time}
상태: 텔레그램 연동 테스트 중

이 메시지가 보인다면 텔레그램 연동이 정상적으로 작동하는 것입니다! ✅
    """.strip()
    
    print("📤 전송할 메시지:")
    print(test_message)
    print()
    
    # 메시지 전송
    result = send_telegram(test_message)
    
    print()
    print("=" * 50)
    if result:
        print("✅ 테스트 성공! 텔레그램에서 메시지를 확인하세요.")
    else:
        print("❌ 테스트 실패! 위의 오류 메시지를 확인하세요.")
    print("=" * 50)


if __name__ == "__main__":
    main()
