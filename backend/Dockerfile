FROM python:3.11-slim
WORKDIR /backend

COPY ./requirements.txt .
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
COPY . .
RUN chmod +x entrypoint.sh
EXPOSE 8000
EXPOSE 8100
CMD ["./entrypoint.sh"]
