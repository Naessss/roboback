### 가상환경 설정
```
py -3.11 -m venv venv
.\venv\Scripts\activate
pip install -r .\requirements.txt
```

### mysql
```
robo_db라는 이름으로 데이터베이스 생성
이름이 만약 다르면 env도 다르게 적용할 것
```

### .env 파일 생성
```
DATABASE_URL=mysql+pymysql://root:1234@localhost:3306/robo_db
SECRET_KEY=1234567890
```

### 데이터베이스 마이그레이션 적용
```
alembic upgrade head
```