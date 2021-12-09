FROM imjeffhi4/wordbreakdown

WORKDIR /app

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "word_breakdown:app", "--host", "0.0.0.0", "--port", "8000"]