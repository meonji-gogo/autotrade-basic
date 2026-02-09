#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
무상태 무한매수법 DryRun 테스트 스크립트

실제 주문을 실행하지 않고, 전략에 따른 예상 주문 목록을 출력합니다.
환경변수를 통해 설정값을 받아서 전략을 실행합니다.
"""

import sys
import os

# src 디렉터리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from strategy import 무상태_무한매수법
from config import SYMBOL, EXCHANGE


def main():
    """
    DryRun 메인 함수
    
    환경변수에서 설정값을 읽어서 전략을 실행하고 결과를 출력합니다.
    """
    
    # ========================================
    # 환경변수 읽기
    # ========================================
    
    symbol = os.getenv("SYMBOL", SYMBOL)  # 기본값: config.py의 SYMBOL
    exchange_code = os.getenv("EXCHANGE", EXCHANGE)  # 필수
    splits = int(os.getenv("SPLITS", "40"))  # 기본값: 40
    take_profit_rate = float(os.getenv("TAKE_PROFIT", "0.10"))  # 기본값: 0.10 (10%)
    big_buy_range = float(os.getenv("BIG_BUY_RANGE", "0.10"))  # 기본값: 0.10 (10%)
    
    # ========================================
    # 전략 실행
    # ========================================
    
    print("\n" + "="*60)
    print("[DRY RUN] 무상태 무한매수법")
    print("="*60 + "\n")
    
    try:
        result = 무상태_무한매수법(
            symbol=symbol,
            exchange_code=exchange_code,
            splits=splits,
            take_profit_rate=take_profit_rate,
            big_buy_range=big_buy_range
        )
        
        # ========================================
        # 결과 출력
        # ========================================
        
        print(f"종목/거래소: {result['symbol']}/{result['exchange']}")
        print(f"거래가능여부: {'가능' if result['tradable'] else '불가능'}")
        print()
        
        print(f"시가: ${result['open_price']:.2f}")
        print(f"현재가: ${result['last_price']:.2f}")
        print()
        
        print(f"보유수량: {result['position_qty']}주")
        if result['avg_price'] > 0:
            print(f"평단가: ${result['avg_price']:.2f}")
        else:
            print(f"평단가: None (포지션 없음)")
        print()
        
        print(f"주문가능금액: ${result['orderable_cash']:.2f}")
        print()
        
        print(f"unit_qty: {result['unit_qty']}주")
        print(f"max_position: {result['max_position']}주")
        print()
        
        print("계산된 기준가:")
        if result['take_profit_price']:
            print(f"  - 익절가: ${result['take_profit_price']:.2f}")
        else:
            print(f"  - 익절가: None (포지션 없음)")
        print(f"  - 큰수기준가: ${result['big_buy_price']:.2f}")
        print()
        
        print("예상 주문:")
        if result['orders']:
            for order in result['orders']:
                side = order['side']
                qty = order['quantity']
                price = order['price']
                order_type = order['order_type']
                comment = order['comment']
                
                if price is not None:
                    print(f"  - {side} {qty}주 @ ${price:.2f} ({order_type}) # {comment}")
                else:
                    print(f"  - {side} {qty}주 ({order_type}) # {comment}")
        else:
            print("  - 예상 주문 없음")
        
        print()
        print("="*60)
        print("[DRY RUN 완료]")
        print("="*60 + "\n")
    
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
