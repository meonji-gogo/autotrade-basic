"""
자동매매 봇 메인 실행 파일

이 프로그램은 다음 작업을 순서대로 수행합니다:
1. 환경변수에서 설정값을 읽어옵니다 (.env 파일)
2. 전략 함수를 실행하여 주문 목록을 생성하고 출력합니다
3. 생성된 주문을 실행합니다

프로그램 실행 중 발생하는 모든 에러는 catch되어 출력됩니다.
향후 텔레그램 알림 기능을 추가할 예정입니다.
"""

import sys
sys.path.append("src")

from config import SYMBOL, EXCHANGE, TRADE_MODE, SPLITS, TAKE_PROFIT, BIG_BUY_RANGE
from strategy import 무상태_무한매수법
from trader import place_overseas_order
from telegram import send_telegram


def convert_exchange_code(exchange_code):
    """
    거래소 코드를 주문 API용 코드로 변환합니다.
    
    조회용 거래소 코드와 주문용 거래소 코드가 다릅니다.
    예: NAS (조회용) -> NASD (주문용)
    
    Parameters:
        exchange_code (str): 조회용 거래소 코드 (예: "NAS", "NYS")
    
    Returns:
        str: 주문용 거래소 코드 (예: "NASD", "NYSE")
    """
    exchange_map = {
        "NAS": "NASD",  # 나스닥
        "NYS": "NYSE",  # 뉴욕
        "AMS": "AMEX",  # 아멕스
        "HKS": "SEHK",  # 홍콩
        "TSE": "TKSE",  # 도쿄
        "SHS": "SHAA",  # 상해
        "SZS": "SZAA"   # 심천
    }
    
    return exchange_map.get(exchange_code, exchange_code)


def main():
    """
    자동매매 봇의 메인 실행 함수입니다.
    
    전체 프로세스:
    1. 환경변수 로드 및 확인
    2. 전략 실행하여 주문 목록 생성
    3. 주문 목록 출력
    4. 각 주문 실행 (현재는 매수 주문만 지원)
    """
    
    try:
        print("\n" + "="*60)
        print("자동매매 봇 시작")
        print("="*60)
        
        # 텔레그램으로 시작 알림 전송
        send_telegram("🚀 자동매매 시작")
        
        # ========================================
        # Step 1: 환경변수 확인
        # ========================================
        print(f"\n[설정 정보]")
        print(f"종목 코드: {SYMBOL}")
        print(f"거래소: {EXCHANGE}")
        print(f"분할 수: {SPLITS}")
        print(f"익절률: {TAKE_PROFIT*100}%")
        print(f"큰수 상승률: {BIG_BUY_RANGE*100}%")
        print(f"거래 모드: {TRADE_MODE}")
        
        # ========================================
        # Step 2: 전략 실행
        # ========================================
        print(f"\n[Step 1] 전략 실행 중...")
        
        strategy_result = 무상태_무한매수법(
            symbol=SYMBOL,
            exchange_code=EXCHANGE,
            splits=SPLITS,
            take_profit_rate=TAKE_PROFIT,
            big_buy_range=BIG_BUY_RANGE
        )
        
        # 전략 결과 출력
        print(f"✓ 전략 실행 완료")
        print(f"  현재가: ${strategy_result['last_price']}")
        print(f"  보유 수량: {strategy_result['position_qty']}주")
        print(f"  평단가: ${strategy_result['avg_price']}")
        print(f"  주문 가능 금액: ${strategy_result['orderable_cash']:.2f}")
        print(f"  단위 수량: {strategy_result['unit_qty']}주")
        
        # ========================================
        # Step 3: 주문 목록 출력
        # ========================================
        orders = strategy_result['orders']
        
        print(f"\n[Step 2] 생성된 주문 목록 ({len(orders)}개)")
        print("-" * 60)
        
        if len(orders) == 0:
            print("생성된 주문이 없습니다.")
            print("\n프로그램을 종료합니다.")
            return
        
        for i, order in enumerate(orders, 1):
            print(f"\n주문 {i}:")
            print(f"  설명: {order['comment']}")
            print(f"  매수/매도: {order['side']}")
            print(f"  주문 유형: {order['order_type']}")
            print(f"  수량: {order['quantity']}주")
            if order['price']:
                print(f"  가격: ${order['price']}")
            else:
                print(f"  가격: 시장가")
        
        # ========================================
        # Step 4: 주문 실행
        # ========================================
        print(f"\n[Step 3] 주문 실행 중...")
        print("-" * 60)
        
        # 주문용 거래소 코드 변환
        order_exchange_code = convert_exchange_code(EXCHANGE)
        
        # 각 주문 실행
        executed_orders = []
        failed_orders = []
        skipped_orders = []
        
        for i, order in enumerate(orders, 1):
            print(f"\n주문 {i}/{len(orders)} 실행: {order['comment']}")
            
            # 현재 매도 주문은 지원하지 않음 (주문 함수가 매수만 지원)
            if order['side'] == "SELL":
                print(f"⊘ 매도 주문은 현재 지원하지 않습니다. 건너뜁니다.")
                skipped_orders.append({
                    "comment": order['comment'],
                    "reason": "매도 주문 미지원"
                })
                # TODO: 매도 주문 API 추가 구현 필요
                continue
            
            try:
                # 주문 가격 설정 (시장가인 경우 0으로 설정)
                order_price = order['price'] if order['price'] else 0
                
                # 주문 실행
                result = place_overseas_order(
                    symbol=SYMBOL,
                    exchange_code=order_exchange_code,
                    order_type=order['order_type'],
                    quantity=order['quantity'],
                    price=order_price,
                    trade_mode=TRADE_MODE
                )
                
                if result:
                    # LIVE 모드일 때 주문번호 저장
                    executed_orders.append({
                        "comment": order['comment'],
                        "odno": result['odno'],
                        "ord_tmd": result['ord_tmd']
                    })
                    print(f"✓ 주문 성공")
                    
                    # 텔레그램으로 주문 성공 알림 전송
                    message = f"""✅ 주문 성공

{order['comment']}
수량: {order['quantity']}주
주문번호: {result['odno']}
시각: {result['ord_tmd']}"""
                    send_telegram(message)
                else:
                    # DRY 모드일 때
                    print(f"✓ 주문 정보 출력 완료")
                
            except Exception as e:
                # 주문 실패 시 에러 출력 및 기록
                error_msg = f"주문 실패: {str(e)}"
                print(f"✗ {error_msg}")
                failed_orders.append({
                    "comment": order['comment'],
                    "error": str(e)
                })
                
                # 텔레그램으로 주문 실패 알림 전송
                message = f"""⚠️ 주문 실패

{order['comment']}
에러: {str(e)}"""
                send_telegram(message)
                
                # 주문 실패 시에도 다음 주문을 계속 진행
                continue
        
        # ========================================
        # Step 5: 결과 요약
        # ========================================
        print(f"\n" + "="*60)
        print(f"자동매매 봇 실행 완료")
        print("="*60)
        
        if TRADE_MODE == "DRY":
            print(f"\n💡 DRY 모드로 실행되었습니다.")
            print(f"   실제 주문은 실행되지 않았으며, 주문 정보만 출력되었습니다.")
            print(f"   총 {len(orders)}개 주문:")
            print(f"   - 출력됨: {len(orders) - len(skipped_orders)}개")
            if skipped_orders:
                print(f"   - 건너뜀: {len(skipped_orders)}개 (매도 주문)")
            print(f"\n   실제 주문을 하려면 .env 파일에서 TRADE_MODE=LIVE로 설정하세요.")
        else:
            print(f"\n✓ LIVE 모드로 실행되었습니다.")
            print(f"   총 {len(orders)}개 주문 중:")
            print(f"   - 성공: {len(executed_orders)}개")
            print(f"   - 실패: {len(failed_orders)}개")
            if skipped_orders:
                print(f"   - 건너뜀: {len(skipped_orders)}개")
            
            if executed_orders:
                print(f"\n[실행된 주문 목록]")
                for order in executed_orders:
                    print(f"  ✓ {order['comment']}: 주문번호 {order['odno']} (시각: {order['ord_tmd']})")
            
            if failed_orders:
                print(f"\n[실패한 주문 목록]")
                for order in failed_orders:
                    print(f"  ✗ {order['comment']}: {order['error']}")
                
                # TODO: 텔레그램으로 실패 요약 전송
                # send_telegram_message(f"⚠️ 주문 실패 {len(failed_orders)}건 발생")
            
            if skipped_orders:
                print(f"\n[건너뛴 주문 목록]")
                for order in skipped_orders:
                    print(f"  ⊘ {order['comment']}: {order['reason']}")
        
        print(f"\n프로그램을 정상적으로 종료합니다.")
        
    except Exception as e:
        # 전체 프로그램 실행 중 예상치 못한 에러 발생
        print(f"\n" + "="*60)
        print(f"✗ 프로그램 실행 중 치명적 에러 발생")
        print("="*60)
        print(f"에러: {str(e)}")
        
        # 텔레그램으로 치명적 에러 알림 전송
        message = f"""🚨 치명적 에러 발생

{str(e)}"""
        send_telegram(message)
        
        # 상세 에러 정보 출력
        import traceback
        print(f"\n[상세 에러 정보]")
        print(traceback.format_exc())
        
        print(f"\n프로그램을 에러와 함께 종료합니다.")
        sys.exit(1)


if __name__ == "__main__":
    main()
