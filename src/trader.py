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
