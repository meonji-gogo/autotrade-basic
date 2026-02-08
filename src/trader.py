# 실제 주문을 실행하는 코드
import requests
from authentication import get_access_token
from config import KIS_APP_KEY, KIS_APP_SECRET, KIS_DOMAIN


def get_overseas_stock_price(symbol, exchange_code="NAS"):
    """
    한국투자증권 API를 사용하여 해외주식의 현재가를 조회합니다.
    
    해외주식 시세는 지연시세(무료)로 제공됩니다.
    - 미국(NAS, NYS): 실시간 지연 없음
    - 기타 지역: 15분 지연
    
    Parameters:
        symbol (str): 종목 코드 (예: "TQQQ", "AAPL", "TSLA")
        exchange_code (str): 거래소 코드
            - NAS: 나스닥 (기본값)
            - NYS: 뉴욕
            - HKS: 홍콩
            - TSE: 도쿄
            - SHS: 상해
            - 기타 코드는 공식 문서 참고
    
    Returns:
        dict: 현재가 정보를 포함한 딕셔너리
              주요 필드:
              - rsym: 종목 코드
              - last: 현재가
              - open: 시가
              - high: 고가
              - low: 저가
              - base: 전일 종가
              - tvol: 거래량
              - tamt: 거래대금
              - perx: PER
              - pbrx: PBR
              - epsx: EPS
              - t_xprc: 원환산 당일 가격
    
    Raises:
        Exception: API 호출 실패 또는 필수 정보 미설정 시 예외 발생
    """
    
    # Step 1: 접근 토큰 획득
    # 한 번 발급한 토큰은 캐싱되어 재사용됩니다
    try:
        token_data = get_access_token()
        access_token = token_data["access_token"]
    except Exception as e:
        raise Exception(f"토큰 획득 실패: {str(e)}")
    
    # Step 2: API 호출 URL 구성
    url = f"{KIS_DOMAIN}/uapi/overseas-price/v1/quotations/price-detail"
    
    # Step 3: 요청 헤더 설정
    # authorization 헤더에 "Bearer" 접두사를 붙여야 합니다
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET,
        "tr_id": "HHDFS76200200"  # 해외주식 현재가상세 조회 API의 거래 ID
    }
    
    # Step 4: Query Parameter 설정
    # 사용자 권한 정보와 조회 조건을 포함합니다
    params = {
        "AUTH": "",  # 사용자 권한 정보 (개인 고객은 빈 값)
        "EXCD": exchange_code,  # 거래소 코드 (NAS = 나스닥)
        "SYMB": symbol  # 종목 코드 (예: TQQQ)
    }
    
    # Step 5: API 호출
    try:
        response = requests.get(
            url, 
            headers=headers, 
            params=params, 
            verify=False  # 자체 서명 인증서 때문에 SSL 검증 비활성화
        )
        response.raise_for_status()  # HTTP 에러 발생 시 예외 던지기
        
        # Step 6: 응답 데이터 추출
        response_data = response.json()
        
        # API 응답이 정상인지 확인
        if response_data.get("rt_cd") != "0":  # rt_cd가 0이면 성공
            msg = response_data.get("msg1", "알 수 없는 에러")
            raise Exception(f"API 호출 실패: {msg}")
        
        # 가격 정보 반환
        return response_data.get("output", {})
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"현재가 조회 실패: {str(e)}")


def get_overseas_stock_quotation(symbol, exchange_code="NAS"):
    """
    한국투자증권 API를 사용하여 해외주식의 현재체결가를 조회합니다.
    
    주문 가능 여부(ordy)를 확인하기 위해 사용합니다.
    
    Parameters:
        symbol (str): 종목 코드 (예: "TQQQ", "AAPL", "TSLA")
        exchange_code (str): 거래소 코드
            - NAS: 나스닥 (기본값)
            - NYS: 뉴욕
            - HKS: 홍콩
            - TSE: 도쿄
            - SHS: 상해
            - SZS: 심천
            - HSX: 호치민
            - HNX: 하노이
            - BAQ: 나스닥(주간거래)
            - BAY: 뉴욕(주간거래)
            - BAA: 아멕스(주간거래)
    
    Returns:
        dict: 현재체결가 정보를 포함한 딕셔너리
              주요 필드:
              - rsym: 실시간조회종목코드 (D+시장구분+종목코드)
              - last: 현재가
              - base: 전일 종가
              - diff: 대비 (현재가 - 전일종가)
              - rate: 등락율
              - sign: 대비기호 (1:상한, 2:상승, 3:보합, 4:하한, 5:하락)
              - tvol: 거래량
              - tamt: 거래대금
              - ordy: 매수가능여부 (주문 가능 여부)
    
    Raises:
        Exception: API 호출 실패 또는 필수 정보 미설정 시 예외 발생
    """
    
    # Step 1: 접근 토큰 획득
    try:
        token_data = get_access_token()
        access_token = token_data["access_token"]
    except Exception as e:
        raise Exception(f"토큰 획득 실패: {str(e)}")
    
    # Step 2: API 호출 URL 구성
    url = f"{KIS_DOMAIN}/uapi/overseas-price/v1/quotations/price"
    
    # Step 3: 요청 헤더 설정
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET,
        "tr_id": "HHDFS00000300"  # 해외주식 현재체결가 조회 API의 거래 ID
    }
    
    # Step 4: Query Parameter 설정
    params = {
        "AUTH": "",  # 사용자 권한 정보 (개인 고객은 빈 값)
        "EXCD": exchange_code,  # 거래소 코드
        "SYMB": symbol  # 종목 코드
    }
    
    # Step 5: API 호출
    try:
        response = requests.get(
            url, 
            headers=headers, 
            params=params, 
            verify=False
        )
        response.raise_for_status()
        
        # Step 6: 응답 데이터 추출
        response_data = response.json()
        
        # API 응답이 정상인지 확인
        if response_data.get("rt_cd") != "0":
            msg = response_data.get("msg1", "알 수 없는 에러")
            raise Exception(f"API 호출 실패: {msg}")
        
        # 현재체결가 정보 반환
        return response_data.get("output", {})
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"현재체결가 조회 실패: {str(e)}")


def _convert_exchange_code(exchange_code):
    """
    API 호출에 사용되는 거래소 코드를 변환합니다.
    
    Parameters:
        exchange_code (str): 사용자 입력 거래소 코드 (NAS, NYS, HKS 등)
    
    Returns:
        tuple: (API 요청용 거래소 코드, 통화 코드)
    """
    exchange_map = {
        "NAS": ("NASD", "USD"),      # 나스닥
        "NYS": ("NYSE", "USD"),      # 뉴욕
        "AMS": ("AMEX", "USD"),      # 아멕스
        "HKS": ("SEHK", "HKD"),      # 홍콩
        "TSE": ("TKSE", "JPY"),      # 도쿄
        "SHS": ("SHAA", "CNY"),      # 상해
        "SZS": ("SZAA", "CNY"),      # 심천
        "HSX": ("HASE", "VND"),      # 베트남 하노이
        "HNX": ("VNSE", "VND"),      # 베트남 호치민
    }
    
    if exchange_code in exchange_map:
        return exchange_map[exchange_code]
    else:
        raise Exception(f"지원하지 않는 거래소 코드입니다: {exchange_code}")


def get_overseas_balance(symbol, exchange_code="NAS"):
    """
    한국투자증권 API를 사용하여 해외주식의 보유 잔고를 조회합니다.
    
    특정 종목의 보유 수량과 평단가 정보를 반환합니다.
    
    Parameters:
        symbol (str): 종목 코드 (예: "TQQQ", "AAPL", "TSLA")
        exchange_code (str): 거래소 코드
            - NAS: 나스닥
            - NYS: 뉴욕
            - AMS: 아멕스
            - HKS: 홍콩
            - TSE: 도쿄
            - SHS: 상해
            - SZS: 심천
            - HSX: 호치민
            - HNX: 하노이
    
    Returns:
        dict: 특정 종목의 잔고 정보
              - symbol: 종목 코드
              - quantity: 보유 수량 (ovrs_cblc_qty)
              - avg_price: 평단가 (pchs_avg_pric)
              - 기타 필드: 해외주식명, 평가손익율, 거래통화코드 등
        
        None: 해당 종목의 잔고가 없을 경우
    
    Raises:
        Exception: API 호출 실패 또는 필수 정보 미설정 시 예외 발생
    """
    
    from config import KIS_ACCOUNT_NO, ACNT_PRDT_CD
    
    # Step 1: 접근 토큰 획득
    try:
        token_data = get_access_token()
        access_token = token_data["access_token"]
    except Exception as e:
        raise Exception(f"토큰 획득 실패: {str(e)}")
    
    # Step 2: 거래소 코드와 통화 코드 변환
    try:
        api_exchange_code, currency_code = _convert_exchange_code(exchange_code)
    except Exception as e:
        raise Exception(f"거래소 코드 변환 실패: {str(e)}")
    
    # Step 3: API 호출 URL 구성
    url = f"{KIS_DOMAIN}/uapi/overseas-stock/v1/trading/inquire-balance"
    
    # Step 4: 요청 헤더 설정
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET,
        "tr_id": "TTTS3012R"  # 해외주식 잔고 조회 API의 거래 ID (실전)
    }
    
    # Step 5: Query Parameter 설정
    params = {
        "CANO": KIS_ACCOUNT_NO,           # 종합계좌번호 (8자리)
        "ACNT_PRDT_CD": ACNT_PRDT_CD,    # 계좌상품코드 (01)
        "OVRS_EXCG_CD": api_exchange_code,  # 해외거래소코드
        "TR_CRCY_CD": currency_code,      # 거래통화코드
        "CTX_AREA_FK200": "",             # 연속조회검색조건200 (초기 조회시 공란)
        "CTX_AREA_NK200": ""              # 연속조회키200 (초기 조회시 공란)
    }
    
    # Step 6: API 호출
    try:
        response = requests.get(
            url, 
            headers=headers, 
            params=params, 
            verify=False
        )
        response.raise_for_status()
        
        # Step 7: 응답 데이터 추출
        response_data = response.json()
        
        # API 응답이 정상인지 확인
        if response_data.get("rt_cd") != "0":
            msg = response_data.get("msg1", "알 수 없는 에러")
            raise Exception(f"API 호출 실패: {msg}")
        
        # Step 8: output1 (잔고 정보 배열)에서 해당 종목 찾기
        output1 = response_data.get("output1", [])
        
        if not output1:
            return None  # 보유 잔고가 없음
        
        # 종목 코드로 해당 항목 찾기
        for item in output1:
            # API에서 반환된 해외상품번호에서 종목 코드 추출
            ovrs_pdno = item.get("ovrs_pdno", "")
            
            # 해외상품번호는 보통 종목코드를 포함하고 있음
            if symbol.upper() in ovrs_pdno.upper():
                return {
                    "symbol": symbol.upper(),
                    "quantity": item.get("ovrs_cblc_qty", "0"),  # 보유 수량
                    "avg_price": item.get("pchs_avg_pric", "0"),  # 평단가
                    "item_name": item.get("ovrs_item_name", ""),  # 해외종목명
                    "eval_rate": item.get("evlu_pfls_rt", "0"),  # 평가손익율
                    "currency": item.get("tr_crcy_cd", ""),  # 거래통화코드
                    "exchange": item.get("ovrs_excg_cd", ""),  # 거래소코드
                    "current_price": item.get("now_pric2", "0"),  # 현재가
                    "eval_amount": item.get("ovrs_stck_evlu_amt", "0")  # 평가금액
                }
        
        # 해당 종목의 잔고가 없음
        return None
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"잔고 조회 실패: {str(e)}")


def get_overseas_purchase_amount(symbol, exchange_code="NAS"):
    """
    한국투자증권 API를 사용하여 해외주식의 매수가능금액을 조회합니다.
    
    주문가능외화금액(ord_psbl_frcr_amt) 정보를 포함하여 반환합니다.
    이 함수는 현재가를 기준으로 매수 가능한 외화 금액을 확인합니다.
    
    Parameters:
        symbol (str): 종목 코드 (예: "TQQQ", "AAPL", "TSLA")
        exchange_code (str): 거래소 코드
            - NAS: 나스닥
            - NYS: 뉴욕
            - AMS: 아멕스
            - HKS: 홍콩
            - TSE: 도쿄
            - SHS: 상해
            - SZS: 심천
            - HSX: 호치민
            - HNX: 하노이
    
    Returns:
        dict: 매수가능금액 정보를 포함한 딕셔너리
              주요 필드:
              - ord_psbl_frcr_amt: 주문가능외화금액 (핵심 정보)
              - max_ord_psbl_qty: 최대주문가능수량
              - ord_psbl_qty: 주문가능수량
              - exrt: 환율
              - tr_crcy_cd: 거래통화코드
              - 기타 필드 참고
    
    Raises:
        Exception: API 호출 실패 또는 필수 정보 미설정 시 예외 발생
    """
    
    from config import KIS_ACCOUNT_NO, ACNT_PRDT_CD
    
    # Step 1: 접근 토큰 획득
    try:
        token_data = get_access_token()
        access_token = token_data["access_token"]
    except Exception as e:
        raise Exception(f"토큰 획득 실패: {str(e)}")
    
    # Step 2: 현재가 조회 (단가 정보 필요)
    # 먼저 현재 가격을 조회하여 OVRS_ORD_UNPR (주문단가)로 사용
    try:
        quotation = get_overseas_stock_quotation(symbol=symbol, exchange_code=exchange_code)
        current_price = quotation.get("last", "0")
        
        if not current_price or current_price == "0":
            raise Exception("현재가 조회 실패: 유효한 가격을 얻을 수 없습니다")
    except Exception as e:
        raise Exception(f"현재가 조회 실패: {str(e)}")
    
    # Step 3: 거래소 코드와 통화 코드 변환
    try:
        api_exchange_code, currency_code = _convert_exchange_code(exchange_code)
    except Exception as e:
        raise Exception(f"거래소 코드 변환 실패: {str(e)}")
    
    # Step 4: API 호출 URL 구성
    url = f"{KIS_DOMAIN}/uapi/overseas-stock/v1/trading/inquire-psamount"
    
    # Step 5: 요청 헤더 설정
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET,
        "tr_id": "TTTS3007R"  # 해외주식 매수가능금액조회 API의 거래 ID (실전)
    }
    
    # Step 6: Query Parameter 설정
    params = {
        "CANO": KIS_ACCOUNT_NO,           # 종합계좌번호 (8자리)
        "ACNT_PRDT_CD": ACNT_PRDT_CD,    # 계좌상품코드 (01)
        "OVRS_EXCG_CD": api_exchange_code,  # 해외거래소코드
        "OVRS_ORD_UNPR": current_price,   # 해외주문단가 (현재가 사용)
        "ITEM_CD": symbol.upper()         # 종목코드
    }
    
    # Step 7: API 호출
    try:
        response = requests.get(
            url, 
            headers=headers, 
            params=params, 
            verify=False
        )
        response.raise_for_status()
        
        # Step 8: 응답 데이터 추출
        response_data = response.json()
        
        # API 응답이 정상인지 확인
        if response_data.get("rt_cd") != "0":
            msg = response_data.get("msg1", "알 수 없는 에러")
            raise Exception(f"API 호출 실패: {msg}")
        
        # Step 9: 매수가능금액 정보 반환
        output = response_data.get("output", {})
        
        if not output:
            raise Exception("매수가능금액 정보를 조회할 수 없습니다")
        
        return {
            "symbol": symbol.upper(),
            "current_price": current_price,  # 조회에 사용한 단가
            "ord_psbl_frcr_amt": output.get("ord_psbl_frcr_amt", "0"),  # 주문가능외화금액 (핵심)
            "max_ord_psbl_qty": output.get("max_ord_psbl_qty", "0"),    # 최대주문가능수량
            "ord_psbl_qty": output.get("ord_psbl_qty", "0"),            # 주문가능수량
            "exrt": output.get("exrt", "0"),                            # 환율
            "tr_crcy_cd": output.get("tr_crcy_cd", ""),                 # 거래통화코드
            "ovrs_ord_psbl_amt": output.get("ovrs_ord_psbl_amt", "0"),  # 해외주문가능금액
            "frcr_ord_psbl_amt1": output.get("frcr_ord_psbl_amt1", "0"), # 외화주문가능금액1
            "ovrs_max_ord_psbl_qty": output.get("ovrs_max_ord_psbl_qty", "0"), # 해외최대주문가능수량
            "sll_ruse_psbl_amt": output.get("sll_ruse_psbl_amt", "0")   # 매도재사용가능금액
        }
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"매수가능금액 조회 실패: {str(e)}")


def get_overseas_order_history(symbol, exchange_code="NAS", days=30):
    """
    한국투자증권 API를 사용하여 해외주식의 최근 주문체결내역을 조회합니다.
    
    최근 N일(기본 30일)의 체결내역을 조회하며, 최신 정보가 먼저 표시됩니다.
    초기 조회만 수행하므로 최대 20건(실전) 또는 15건(모의)까지만 조회됩니다.
    
    Parameters:
        symbol (str): 종목 코드 (예: "TQQQ", "AAPL", "TSLA")
        exchange_code (str): 거래소 코드
            - NAS: 나스닥
            - NYS: 뉴욕
            - AMS: 아멕스
            - HKS: 홍콩
            - TSE: 도쿄
            - SHS: 상해
            - SZS: 심천
            - HSX: 호치민
            - HNX: 하노이
        days (int): 조회 기간 (기본 30일)
    
    Returns:
        list: 주문체결내역 배열 (최신순으로 정렬)
              각 항목의 필드:
              - ord_dt: 주문일자
              - prdt_name: 상품명 (종목명)
              - sll_buy_dvsn_cd_name: 매도매수구분 (매도/매수)
              - ft_ord_qty: 주문수량
              - ft_ccld_qty: 체결수량 (핵심 정보)
              - ft_ccld_unpr3: 체결단가
              - ft_ccld_amt3: 체결금액
              - prcs_stat_name: 처리상태
              - 기타 필드 참고
        
        []: 체결내역이 없을 경우 빈 배열
    
    Raises:
        Exception: API 호출 실패 또는 필수 정보 미설정 시 예외 발생
    """
    
    from config import KIS_ACCOUNT_NO, ACNT_PRDT_CD
    from datetime import datetime, timedelta
    
    # Step 1: 접근 토큰 획득
    try:
        token_data = get_access_token()
        access_token = token_data["access_token"]
    except Exception as e:
        raise Exception(f"토큰 획득 실패: {str(e)}")
    
    # Step 2: 날짜 계산 (현지시각 기준 - 한국시간으로 계산)
    today = datetime.now()
    start_date = today - timedelta(days=days)
    
    ord_end_dt = today.strftime("%Y%m%d")
    ord_strt_dt = start_date.strftime("%Y%m%d")
    
    # Step 3: 거래소 코드와 통화 코드 변환
    try:
        api_exchange_code, currency_code = _convert_exchange_code(exchange_code)
    except Exception as e:
        raise Exception(f"거래소 코드 변환 실패: {str(e)}")
    
    # Step 4: API 호출 URL 구성
    url = f"{KIS_DOMAIN}/uapi/overseas-stock/v1/trading/inquire-ccnl"
    
    # Step 5: 요청 헤더 설정
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET,
        "tr_id": "TTTS3035R"  # 해외주식 주문체결내역 조회 API의 거래 ID (실전)
    }
    
    # Step 6: Query Parameter 설정
    params = {
        "CANO": KIS_ACCOUNT_NO,           # 종합계좌번호 (8자리)
        "ACNT_PRDT_CD": ACNT_PRDT_CD,    # 계좌상품코드 (01)
        "PDNO": symbol.upper(),           # 상품번호 (종목 코드 - API 레벨에서 필터링)
        "ORD_STRT_DT": ord_strt_dt,       # 주문시작일자
        "ORD_END_DT": ord_end_dt,         # 주문종료일자
        "SLL_BUY_DVSN": "00",             # 매도매수구분 (00: 전체)
        "CCLD_NCCS_DVSN": "01",           # 체결미체결구분 (01: 체결만)
        "OVRS_EXCG_CD": api_exchange_code,  # 해외거래소코드
        "SORT_SQN": "AS",                 # 정렬순서 (AS: 역순, 최신이 먼저)
        "ORD_DT": "",                     # 주문일자 (Null)
        "ORD_GNO_BRNO": "",               # 주문채번지점번호 (Null)
        "ODNO": "",                       # 주문번호 (Null)
        "CTX_AREA_NK200": "",             # 연속조회키200 (초기조회)
        "CTX_AREA_FK200": ""              # 연속조회검색조건200 (초기조회)
    }
    
    # Step 7: API 호출
    try:
        response = requests.get(
            url, 
            headers=headers, 
            params=params, 
            verify=False
        )
        response.raise_for_status()
        
        # Step 8: 응답 데이터 추출
        response_data = response.json()
        
        # API 응답이 정상인지 확인
        if response_data.get("rt_cd") != "0":
            msg = response_data.get("msg1", "알 수 없는 에러")
            raise Exception(f"API 호출 실패: {msg}")
        
        # Step 9: 주문체결내역 정보 추출
        output = response_data.get("output", [])
        
        if not output:
            return []  # 체결내역이 없음
        
        # 필요한 필드만 추출하여 정렬된 결과 반환
        order_history = []
        for item in output:
            order_history.append({
                "ord_dt": item.get("ord_dt", ""),              # 주문일자
                "ord_tmd": item.get("ord_tmd", ""),            # 주문시각
                "prdt_name": item.get("prdt_name", ""),        # 상품명 (종목명)
                "sll_buy_dvsn_cd_name": item.get("sll_buy_dvsn_cd_name", ""),  # 매도/매수 (핵심)
                "ft_ord_qty": item.get("ft_ord_qty", "0"),     # 주문수량
                "ft_ccld_qty": item.get("ft_ccld_qty", "0"),   # 체결수량 (핵심)
                "ft_ccld_unpr3": item.get("ft_ccld_unpr3", "0"),  # 체결단가
                "ft_ccld_amt3": item.get("ft_ccld_amt3", "0"),    # 체결금액
                "nccs_qty": item.get("nccs_qty", "0"),         # 미체결수량
                "prcs_stat_name": item.get("prcs_stat_name", ""),  # 처리상태
                "tr_mket_name": item.get("tr_mket_name", ""),  # 거래시장명
                "tr_crcy_cd": item.get("tr_crcy_cd", ""),      # 거래통화코드
                "odno": item.get("odno", ""),                  # 주문번호
                "ovrs_excg_cd": item.get("ovrs_excg_cd", "")   # 거래소코드
            })
        
        # Step 10: 데이터 정리 및 반환
        # API에서 이미 해당 종목으로 필터링된 결과를 받았습니다
        return order_history
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"주문체결내역 조회 실패: {str(e)}")
