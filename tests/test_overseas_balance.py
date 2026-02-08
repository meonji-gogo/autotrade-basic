"""
해외주식 잔고 조회 API 테스트

이 테스트는 해외주식 잔고 API를 호출하여
특정 종목의 보유 수량과 평단가를 확인합니다.
"""

import sys
import os
from pathlib import Path

# src 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from trader import get_overseas_balance
from config import SYMBOL, EXCHANGE


def test_overseas_balance():
    """
    해외주식 잔고 조회 API 호출 테스트
    
    테스트 내용:
    - 환경변수에서 읽은 SYMBOL, EXCHANGE를 사용하여 API 호출
    - 보유 수량과 평단가 확인
    - 모든 응답 필드 출력
    """
    
    print("=" * 80)
    print("해외주식 잔고 조회 API 테스트")
    print(f"종목 코드: {SYMBOL} | 거래소: {EXCHANGE}")
    print("=" * 80)
    
    try:
        # API 호출
        result = get_overseas_balance(symbol=SYMBOL, exchange_code=EXCHANGE)
        
        # 결과 검증
        if result is None:
            print("\n⚠️ 해당 종목의 보유 잔고가 없습니다.")
            print("종목 코드 또는 거래소 코드를 확인해주세요.")
            return True  # 이는 API 호출이 성공했지만 잔고가 없는 정상적인 경우
        
        print("\n✅ API 호출 성공!\n")
        
        # 핵심 정보 출력
        print("🔍 핵심 정보:")
        print("-" * 80)
        print(f"  종목 코드 (symbol):          {result.get('symbol', 'N/A')}")
        print(f"  종목명 (item_name):         {result.get('item_name', 'N/A')}")
        
        # 보유 수량과 평단가 (가장 중요한 정보)
        print("\n📊 보유 정보:")
        print("-" * 80)
        quantity = result.get("quantity", "0")
        avg_price = result.get("avg_price", "0")
        
        print(f"  보유 수량 (quantity):        {quantity} 주")
        print(f"  평단가 (avg_price):          {avg_price}")
        
        # 평가 정보
        print("\n💰 평가 정보:")
        print("-" * 80)
        current_price = result.get("current_price", "0")
        eval_rate = result.get("eval_rate", "0")
        eval_amount = result.get("eval_amount", "0")
        
        print(f"  현재가 (current_price):     {current_price}")
        print(f"  평가손익율 (eval_rate):     {eval_rate}%")
        print(f"  평가금액 (eval_amount):     {eval_amount}")
        
        # 거래 정보
        print("\n🌍 거래 정보:")
        print("-" * 80)
        currency = result.get("currency", "")
        exchange = result.get("exchange", "")
        
        print(f"  거래통화 (currency):        {currency}")
        print(f"  거래소 (exchange):          {exchange}")
        
        # 전체 응답 데이터
        print("\n" + "=" * 80)
        print("📋 전체 응답 데이터:")
        print("=" * 80)
        for key, value in sorted(result.items()):
            print(f"  {key:25s}: {value}")
        
        print("\n" + "=" * 80)
        print("✅ 테스트 완료")
        print("=" * 80)
        
        return True
    
    except Exception as e:
        print(f"❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_overseas_balance()
    sys.exit(0 if success else 1)
