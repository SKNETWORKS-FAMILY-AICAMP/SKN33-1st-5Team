# MySQL 연결
import pymysql

def get_connection():
    """
    MySQL 데이터베이스에 연결하고 connection 객체를 반환하는 함수
    """
    try:
        conn = pymysql.connect(
            host='localhost',      # DB 주소 (로컬PC 환경이면 보통 localhost 또는 127.0.0.1)
            user='skn_ai',           # DB 사용자 아이디
            password='1234',   # DB 비밀번호 (본인 설정에 맞게 변경)
            database='cardb',      # 사용할 데이터베이스 스키마 이름 (ERD 기준 예시)
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor  # 데이터를 딕셔너리 형태로 편하게 가져오는 옵션
        )
        return conn
    except Exception as e:
        print(f" 데이터베이스 연결 실패: {e}")
        return None