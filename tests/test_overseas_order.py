"""
해외주식 주문 테스트 스크립트

이 스크립트는 해외주식 주문 함수를 테스트합니다.
- TQQQ 종목을 LIMIT 주문과 LOC 주문으로 테스트
- 현재가 API를 호출하여 실제 가격으로 주문
- TRADE_MODE에 따라 DRY 또는 LIVE 모드로 실행
"""

import sys
sys.path.append("src")

from trader import place_overseas_order, get_overseas_stock_price
from config import SYMBOL, EXCHANGE, TRADE_MODE


def test_overseas_order():
    """
    해외주식 주문 테스트를 실행합니다.
    
    1. TQQQ의 현재가를 조회합니다
    2. LIMIT 주문 (지정가) 테스트
    3. LOC 주문 (장마감지정가) 테스트
    """
    
    print("\n" + "="*60)
    print("해외주식 주문 테스트 시작")
    print("="*60)
    
    # 환경변수 확인
    print(f"\n[설정 정보]")
    print(f"종목 코드: {SYMBOL}")
    print(f"거래소: {EXCHANGE}")
    print(f"거래 모드: {TRADE_MODE}")
    
    try:
        # Step 1: 현재가 조회
        print(f"\n[Step 1] {SYMBOL} 현재가 조회 중...")
        
        # 거래소 코드 변환: NAS -> NASD
        exchange_map = {
            "NAS": "NASD",  # 나스닥
            "NYS": "NYSE",  # 뉴욕
            "AMS": "AMEX"   # 아멕스
        }
        
        # 주문용 거래소 코드
        order_exchange_code = exchange_map.get(EXCHANGE, EXCHANGE)
        
        # 현재가 조회용 거래소 코드는 원래 코드 사용
        price_data = get_overseas_stock_price(SYMBOL, EXCHANGE)
        
        current_price = float(price_data.get("last", "0"))
        
        if current_price == 0:
            print("현재가 조회에 실패했습니다.")
            return
        
        print(f"✓ 현재가: ${current_price}")
        print(f"  시가: ${price_data.get('open', 'N/A')}")
        print(f"  고가: ${price_data.get('high', 'N/A')}")
        print(f"  저가: ${price_data.get('low', 'N/A')}")
        
        # Step 2: LIMIT 주문 테스트
        print(f"\n[Step 2] LIMIT 주문 (지정가) 테스트")
        print("-" * 60)
        
        try:
            result_limit = place_overseas_order(
                symbol=SYMBOL,
                exchange_code=order_exchange_code,
                order_type="LIMIT",
                quantity=1,
                price=current_price,
                trade_mode=TRADE_MODE
            )
            
            if result_limit:
                print(f"✓ LIMIT 주문 성공")
                print(f"  주문번호: {result_limit.get('odno', 'N/A')}")
            else:
                print(f"✓ LIMIT 주문 정보 출력 완료 (DRY 모드)")
                
        except Exception as e:
            print(f"✗ LIMIT 주문 실패: {str(e)}")
        
        # Step 3: LOC 주문 테스트
        print(f"\n[Step 3] LOC 주문 (장마감지정가) 테스트")
        print("-" * 60)
        
        try:
            result_loc = place_overseas_order(
                symbol=SYMBOL,
                exchange_code=order_exchange_code,
                order_type="LOC",
                quantity=1,
                price=current_price,
                trade_mode=TRADE_MODE
            )
            
            if result_loc:
                print(f"✓ LOC 주문 성공")
                print(f"  주문번호: {result_loc.get('odno', 'N/A')}")
            else:
                print(f"✓ LOC 주문 정보 출력 완료 (DRY 모드)")
                
        except Exception as e:
            print(f"✗ LOC 주문 실패: {str(e)}")
        
        # 결과 요약
        print(f"\n" + "="*60)
        print("테스트 완료")
        print("="*60)
        
        if TRADE_MODE == "DRY":
            print("\n💡 DRY 모드로 실행되었습니다.")
            print("   실제 주문은 실행되지 않았으며, 주문 정보만 출력되었습니다.")
            print("   실제 주문을 하려면 .env 파일에서 TRADE_MODE=LIVE로 설정하세요.")
        else:
            print("\n⚠️  LIVE 모드로 실행되었습니다.")
            print("   실제 주문이 실행되었습니다. 주문 내역을 확인하세요.")
        
    except Exception as e:
        print(f"\n✗ 테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_overseas_order()
