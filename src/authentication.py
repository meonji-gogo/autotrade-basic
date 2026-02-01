# 한국투자증권 API 인증을 담당하는 파일
import requests
from config import KIS_APP_KEY, KIS_APP_SECRET, KIS_DOMAIN


def get_access_token():
    """
    한국투자증권 API에서 access token을 발급받습니다.
    
    이 함수는 한국투자증권의 OAuth2 Client Credentials 절차를 따릅니다.
    - token은 발급 후 24시간 동안 유효합니다
    - 6시간 이내에 재발급 요청하면 이전 token을 반환합니다
    
    Returns:
        dict: access token과 관련 정보를 포함한 딕셔너리
              {
                  'access_token': 'Bearer...',
                  'token_type': 'Bearer',
                  'expires_in': 초 단위 유효기간,
                  'access_token_token_expired': '2024-01-01 00:00:00' 형식의 유효기간
              }
    
    Raises:
        Exception: API 호출 실패 또는 필수 환경변수 미설정 시 예외 발생
    """
    
    # 환경변수가 설정되어 있는지 확인
    if not KIS_APP_KEY or not KIS_APP_SECRET:
        raise Exception(
            "환경변수 KIS_APP_KEY와 KIS_APP_SECRET이 설정되어야 합니다. "
            ".env 파일을 확인해주세요."
        )
    
    # API 호출에 필요한 정보 준비
    url = f"{KIS_DOMAIN}/oauth2/tokenP"
    
    # 요청 헤더 설정
    headers = {
        "Content-Type": "application/json; charset=UTF-8"
    }
    
    # 요청 바디 설정
    # grant_type은 항상 "client_credentials"로 고정됩니다
    body = {
        "grant_type": "client_credentials",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET
    }
    
    # API 호출
    try:
        response = requests.post(url, json=body, headers=headers, verify=False)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 던지기
        
        # 응답 데이터 추출
        token_data = response.json()
        
        return token_data
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"토큰 발급 실패: {str(e)}")
