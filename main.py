import os
from dotenv import load_dotenv


def main():
    # .env 파일에서 환경변수 로드
    load_dotenv()
    
    # 환경변수 읽기
    app_name = os.getenv("APP_NAME")
    env = os.getenv("ENV")
    
    # 환경변수 출력 (정상 로드 확인용)
    print(f"앱 이름: {app_name}")
    print(f"실행 환경: {env}")
    print("자동매매 프로그램이 시작되었습니다!")


if __name__ == "__main__":
    main()
